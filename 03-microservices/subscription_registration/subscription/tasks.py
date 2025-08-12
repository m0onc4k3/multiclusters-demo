# celetry -A subscripton worker --loglevel=info
from celery import shared_task
from django.core.mail import send_mail
from rapidfuzz import fuzz
from subscription.models import Address
from .host import get_subscription_url
from datetime import datetime
import requests
import logging

logger = logging.getLogger(__name__)
# decorates the match_address_task function so that 
# the function becomes a Celery shared task
@shared_task
def process_address_matching(form_data, access_token):
    # retrieve all addresses from the MongoDB collection into a Python list
    api_url = get_subscription_url()
    #headers = {'Cookie': f'access_token={access_token}'}
    try:
        response = requests.get(api_url, cookies={'access_token': access_token})
        logger.info(f"GET response status: {response.status_code}")
        # print('GET RESPONSE',response.status_code)

        best_match = form_data["address"]
        best_score = 0
        min_score = 70

        if response.status_code == 200:
            addresses = response.json()
            current_address = form_data["address"]

            for addr in addresses:
                if 'address' in addr and addr['address']:
                    score = fuzz.ratio(current_address, addr["address"])
                    if score > best_score and score >= min_score:
                        best_score = score
                        best_match = addr["address"]
                    if best_score == 100:
                        break
        else:
            logger.error(f"Failed to fetch addresses: status={response.status_code}, response={response.text}")
    except requests.RequestException as e:
        logger.error(f"GET request failed: {str(e)}")
        best_match = form_data["address"]  # Fallback to original address

    # Post Updated data to API
    # Step 3: Update the address if matched
    if best_match != form_data["address"]:
        form_data["address"] = best_match
    
    form_data["created_at"] = datetime.utcnow().isoformat()
    
    try:
        post_response = requests.post(api_url, json=form_data, cookies={'access_token': access_token})
        logger.info(f"POST response status: {post_response.status_code}")
        logger.debug(f"POST response content: {post_response.text}")

        if post_response.status_code == 201:
            print(f"New address inserted for {form_data['name']} | {form_data['address']}")
            send_email_task.delay(form_data['name'], form_data["email"])
            return post_response.json()
        else:
            logger.error(f"Failed to insert updated data: status={post_response.status_code}, response={post_response.text}")
            return {"error": f"POST failed with status {post_response.status_code}"}
    except requests.RequestException as e:
        logger.error(f"POST request failed: {str(e)}")
        return {"error": str(e)}

@shared_task
def send_email_task(name, email):
    send_mail(
        "Your subscription",
        f"Dear {name},\n\nThanks for subscribing to our magazine! You'll receive the latest edition of our magazine within three days.\n\nCM Publishers",
        "magazine@cm-publishers.com",
        [email],
        fail_silently=False,
    )