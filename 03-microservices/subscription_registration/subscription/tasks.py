# celetry -A subscripton worker --loglevel=info
import json
import redis
import requests
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from rapidfuzz import fuzz
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .host import get_subscription_url
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

redis_client = redis.Redis(host=settings.REDIS_HOST, port=6379, db=2)  # Use DB 2 for addresses

@retry(
        stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(requests.RequestException),
    before_sleep=lambda retry_state: logger.warning(f'Retrying API GET: attempt {retry_state.attempt_number}')
    )
def get_addresses(api_url, cookies):
    cache_key = 'base_addresses'
    addresses = redis_client.get(cache_key)
    if addresses is None:
        # api_url = get_subscription_url()    
        logger.info(f'API URL: {api_url}\nCOOKIES: {cookies}')
        try:
            response = requests.get(api_url, cookies=cookies)
            response.raise_for_status() # Raise exception for non-200 status
            # if response.status_code == 200:
            addresses = response.json()
            # Extract unique addresses (assuming list of dicts with 'address' key)
            unique_addresses = list(set(addr.get('address') for addr in addresses if addr.get('address')))
            redis_client.set(cache_key, json.dumps(unique_addresses), ex=3600)  # Cache for 1 hour
            return unique_addresses
        except requests.RequestException as e:
            logger.error(f"GET request failed: {str(e)}, response: {response.text if 'response' in locals() else 'No response'}")
            raise 
    else:
        logger.info("Retrieved addresses from Redis cache")
        return json.loads(addresses)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(requests.RequestException),
    before_sleep=lambda retry_state: logger.warning(f'Retrying API POST: attempt {retry_state.attempt_number}')
    )

def post_address(api_url, cookies, form_data):
    logger.info(f"POSTing to API URL: {api_url}\nForm data: {form_data}\nCookies: {cookies}")
    try:
        response = requests.post(api_url, json=form_data, cookies=cookies, timeout=10)
        response.raise_for_status()
        logger.info(f"POST response status: {response.status_code}, response: {response.json()}")
    # if post_response.status_code == 201:
    #     logger.info(f"New address inserted for {form_data['name']} | {form_data['address']}")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"POST request failed: {str(e)}, response: {response.text if 'response' in locals() else 'No response'}")
        raise 
    # return post_response.json()



# decorates the match_address_task function so that 
# the function becomes a Celery shared task

@shared_task
def process_address_matching(form_data, access_token):
    api_url = get_subscription_url()
    cookies = {'access_token': access_token}
    logger.info(f"Processing form data: {form_data}\nAPI URL: {api_url}\nCookies: {cookies}")

    # retrieve all addresses from the MongoDB collection into a Python            
    try:
        unique_addresses = get_addresses(api_url, cookies)
        current_address = form_data['address']

        best_match = current_address # form_data["address"]
        best_score = 0
        min_score = 70

        for addr in unique_addresses:
            # if 'address' in addr and addr['address']:
            score = fuzz.ratio(current_address, addr)
            if score > best_score and score >= min_score:
                best_score = score
                best_match = addr
            if best_score == 100:
                break
        if best_match != current_address:
            form_data["address"] = best_match
        form_data["created_at"] = datetime.utcnow().isoformat()
        
        post_result = post_address(api_url, cookies, form_data)
        send_email_task.delay(form_data['name'], form_data['address'], form_data['email'])
        logger.info(f"Task completed successfully: {post_result}")
        return post_result
    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        raise Exception(f'Address matching task failes: {str(e)}')

@shared_task
def send_email_task(name, address, email):
    try:
        send_mail(
            "Your subscription",
            f"""Dear {name},\n\nThanks for subscribing to our magazine!
            \nWe registered the subscription at this address:\n{address}.
            \nAnd you'll receive the latest edition of our magazine within three days.
            \nCM Publishers""",
            "magazine@cm-publishers.com",
            [email],
            fail_silently=False,
        )
        logger.info(f"Email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send email to {email}: {str(e)}")
        raise