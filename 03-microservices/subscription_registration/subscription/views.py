from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.utils.decorators import method_decorator

#from django.http import JsonResponse
#from django.views import View

#from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
#from .forms import SubscriptionForm, LoginForm
#from .models import Address

from django.shortcuts import redirect
from django.conf import settings
from .forms import SubscriptionForm
from .host import get_cookies_url, get_subscription_url
from .tasks import process_address_matching

#from django.contrib.auth import authenticate, login

import requests
import logging

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import WebApplicationClient

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class OIDCLoginView(FormView):
    template_name = "subscription/login.html"
    form_class = SubscriptionForm
    success_url = "/oidc/callback/"

    def get(self, request):
        client = WebApplicationClient(settings.KEYCLOAK_CLIENT_ID)
        oauth = OAuth2Session(
            client_id=settings.KEYCLOAK_CLIENT_ID, 
            redirect_uri=settings.KEYCLOAK_REDIRECT_URI,
            scope=['openid','profile','email']
            )
        authorization_url, state = oauth.authorization_url(
            f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/auth"
            )
        request.session['oidc_state'] = state # triggers a write opperation in db.sqlite3
        request.session.modified = True # Ensure session is saved
        logger.info(f'Redirecting to Keycloak with state: {state}')
        return redirect(authorization_url)

class OIDCCallbackView(FormView):
    template_name = "subscription/login.html"
    form_class = SubscriptionForm
    success_url = "/subscription/"

    def get(self, request):
        oauth = OAuth2Session(
            client_id=settings.KEYCLOAK_CLIENT_ID, 
            redirect_uri=settings.KEYCLOAK_REDIRECT_URI, 
            state=request.session['oidc_state'])
        try:    
            token = oauth.fetch_token(
                f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/token",
                client_secret=settings.KEYCLOAK_CLIENT_SECRET,
                authorization_response=request.build_absolute_uri(),
                verify=False #[ ] Disable SSL verification for self-signed cert (dev only)
            )
            introspection_url = f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/token/introspect"
            introspection_data = {
                'token': token['access_token'],
                'token_type_hint': 'access_token',
                'client_id': settings.KEYCLOAK_CLIENT_ID,
                'client_secret': settings.KEYCLOAK_CLIENT_SECRET
            }
            introspection_response = requests.post(introspection_url, data=introspection_data, verify=False)
            if introspection_response.status_code != 200:
                logger.error(f'Token introspection failed: {introspection_response.text}')
                # introspected = response.json()
                raise Exception('Token introspection failed')
            introspected = introspection_response.json()
            if not introspected.get('active', False):
                raise Exception('Token is not active')
            logger.info('Token instrospection successful')
            # else:
            #     raise Exception('Introspection failed')
            # Set cookies
            response = redirect(self.get_success_url())
            response.set_cookie('access_token', token['access_token'], max_age=token.get('expires_in', 3600), httponly=True, secure=True, samesite='Lax')
            response.set_cookie('refresh_token', token['refresh_token'], max_age=token.get('expires_in', 86400), httponly=True, secure=True, samesite='Lax')
            logger.info('Keycloak tokens set in cookies')
            # Clear oidc_state from session
            request.session.pop('oidc_state', None)
            request.session.modified = True
            return response
        except Exception as e:
            logger.error(f'Keycloak token fetch failed: {str(e)}')
            return redirect('subscription:login')

# class LoginView(FormView):
#     template_name = "subscription/login.html"
#     form_class = LoginForm
#     success_url = "/subscription/"

#     def form_valid(self, form):
#         cookies_address = get_cookies_url()
#         username = form.cleaned_data['username']
#         password = form.cleaned_data['password']
#         user = authenticate(self.request, username=username, password=password)
#         if user is not None:
#             login(self.request, user)  # Set Django session
#             logger.info(f"User {username} authenticated successfully in Django")

#             try:
#                 response = requests.post(
#                     cookies_address,
#                     json={'username': username, 'password': password}
#                 )
#                 logger.info(f"API response status: {response.status_code}")
#                 # logger.info(f"API response content: {response.text}")
#                 # logger.info(f"API response cookies: {response.cookies.get_dict()}")
#                 # logger.info(f"API response headers: {dict(response.headers)}")
            
#                 if response.status_code == 200:
#                     # Forward cookies from API to client
#                     # django_response = redirect(self.get_success_url())

#                     # response.cookies is a RequestsCookieJar object
#                     access_token = response.cookies.get('access_token')
#                     refresh_token = response.cookies.get('refresh_token')
                    
#                     if not access_token or not refresh_token:
#                         logger.error("No cookies received from API")
#                         form.add_error(None, "Failed to obtain authentication cookies")
#                         return self.form_invalid(form)
                    
#                     # Handle 'next' parameter if present
#                     next_url = self.request.GET.get('next', self.get_success_url())
#                     logger.info(f"Redirecting to: {next_url}")
#                     if next_url == '/success/':
#                         logger.info("Overriding next=/success/ to /subscription/")
#                         next_url = self.get_success_url()
#                     logger.info(f"Redirecting to: {next_url}")
                    
#                     django_response = redirect(next_url)
                    
#                     django_response.set_cookie(
#                         key='access_token',
#                         value=access_token,
#                         max_age=60 * 60,
#                         httponly=True,
#                         secure=False,  # Set to True in production
#                         samesite='Lax',
#                     )
#                     django_response.set_cookie(
#                         key='refresh_token',
#                         value=refresh_token,
#                         max_age=24 * 60 * 60,
#                         httponly=True,
#                         secure=False,  # Set to True in production
#                         samesite='Lax',
#                     )
#                     return django_response
#                 else:
#                     logger.error(f"API token request failed: status={response.status_code}, response={response.text}")
#                     form.add_error(None, "Failed to obtain authentication token")
#                     return self.form_invalid(form)
            
#             except requests.RequestException as e:
#                 logger.error(f"API request error: {str(e)}")
#                 form.add_error(None, f"API request failed: {str(e)}")
#                 return self.form_invalid(form)

#         else:
#             logger.error(f"Django authentication failed for user: {username}")
#             form.add_error(None, "Invalid username or password")
#             return self.form_invalid(form)

class SubscriptionFormView(FormView):
    template_name = "subscription/subscription.html"
    form_class = SubscriptionForm
    success_url = "/success/"
    #login_url = "/login/"

    def get(self, request, *args, **kwargs):
        access_token = request.COOKIES.get('access_token')
        if not access_token:
            logger.error(f'No access_token found in request COOKIES: {request.COOKIES}')
            return redirect('subscription:login')
        # try:
        #     # Verify token with Keycloak
        #     oauth = OAuth2Session(client_id=settings.KEYCLOAK_CLIENT_ID)
        #     token_info = oauth.introspect_token(
        #         token=access_token,
        #         token_type_hint='access_token',
        #         token_endpoint=f'{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/token/introspect',
        #         client_secret=settings.KEYCLOAK_CLIENT_SECRET
        #     )
        #     if not token_info.get('active', False):
        #         logger.error('Access token is invalid or expired')
        #         return redirect('subscription:login')
        # except Exception as e:
        #     logger.error(f'Token introspection failed: {str(e)}')
        #     return redirect('subscription:login')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        access_token = self.request.COOKIES.get("access_token") 
        if not access_token:
            logger.error(f"No access_token found in request COOKIES: {self.request.COOKIES}")
            form.add_error(None, "Authentication token missing. Please log in again.")
            return self.form_invalid(form)

        #logger.info(f"Form valid, processing data: {form.cleaned_data}")
        form_data = {
            'name': form.cleaned_data['name'],
            'address': form.cleaned_data['address'],
            'postalcode': form.cleaned_data['postalcode'],
            'city': form.cleaned_data['city'],
            'country': form.cleaned_data['country'],
            'email': form.cleaned_data['email']
        }
    
        logger.info(f"Queuing Celery task with form_data: {form_data}, access_token: {access_token[:10]}...")
        process_address_matching.delay(form_data, access_token)
        # Set session flag for successful form submission
        self.request.session['form_submitted'] = True
        logger.info("Session form_submitted set to True")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        logger.error(f"Form invalid, errors: {form.errors}")
        return super().form_invalid(form)

@method_decorator(cache_page(60*30), name='dispatch')
class SuccessView(TemplateView):
    template_name = "subscription/success.html"
    #login_url = "/login/"

    def get(self, request, *args, **kwargs):
        # Check if form was submitted
        if not request.session.get('form_submitted', False):
            logger.warning("Access to success page denied: no form submission")
            raise PermissionDenied("You must submit the subscription form first.")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # from django.core.cache import cache
        context = super().get_context_data(**kwargs)
        magazines = cache.get('magazines')
        if magazines is None:
            logger.warning('Magazines not found in cache, loading defaults')
            magazines = [
                {'title': 'Django Demystified', 'description': 'Go beyond the standard Django features and learn features only experienced pros know.'},
                {'title': 'Microservices Magic', 'description': 'Take yourself to the next level as a developer and master microservices.'},
                {'title': 'Python to Perfection', 'description': 'Squeeze every last bit out of Python with the very latest Python features, tips and tricks.'}
            ]
            cache.set('magazines', magazines, timeout=None)  # Cache indefinitely
        context['magazines'] = magazines
        return context

# from django.http import JsonResponse
# from django.views import View

# class HealthCheckView(View):
#     def get(self, request):
#         health_status = {
#             "status": "healthy",
#             "mongodb_cert_exists": mongodb_cert_manager.mongodb_cert_file and 
#                                  mongodb_cert_manager.mongodb_cert_file.exists(),
#             "vault_secrets_loaded": Path(os.getenv('VAULT_SECRETS_PATH', '/vault/secrets')).exists()
#         }
#         try:
#             # Test MongoDB connection
#             from subscription.mongodb import get_collection
#             get_collection().database.command('ping')  # Lightweight test
#             health_status["mongodb_connection"] = "ok"
#         except Exception as e:
#             health_status["mongodb_connection"] = f"error: {str(e)}"
#             health_status["status"] = "unhealthy"
#         status_code = 200 if health_status["status"] == "healthy" else 503
#         return JsonResponse(health_status, status=status_code)


