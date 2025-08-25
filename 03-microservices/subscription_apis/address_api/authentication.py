import os
import logging
import jwt
import requests
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)

class JWTUser:
    def __init__(self, payload):
        self.payload = payload
        self.id = payload.get('sub')
        self.username = payload.get('preferred_username')
        self.email = payload.get('email')

    @property
    def is_authenticated(self):
        return True # Always True for successfully decoded tokens

    def __str__(self):
        return self.username or self.id

class KeycloakJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        # if not auth_header.startswith('Bearer '):
        #     return None
        # token = auth_header[len('Bearer '):].strip()
        
        token = request.COOKIES.get('access_token')
        if not token:
            logger.info("No access token found in cookies")
            return None # No token, let other auth methods handle
        
        try:
            # # Fetch JWKS from Keycloak
            # jwks_url = f"{os.environ.get('KEYCLOAK_SERVER_URL', 'https://keycloak:8443')}/realms/{os.environ.get('KEYCLOAK_REALM', 'subscription_realm')}/protocol/openid-connect/certs"
            ca_cert = os.environ.get('KEYCLOAK_CA_CERT', '/app/certs/keycloak.crt')
            # response = requests.get(jwks_url, verify=ca_cert)
            # response.raise_for_status()
            # jwks = response.json()
            jwks_url = f'{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/certs'
            jwks_response = requests.get(jwks_url, verify=ca_cert) #[ ] Disable (False) SSL verification for self-signed cert (dev only)
            jwks_response.raise_for_status()
            jwks = jwks_response.json()
            logger.info(f"JWKS fetched: {jwks['keys']}")

            # Get token header
            headers = jwt.get_unverified_header(token)
            kid = headers.get('kid')
            logger.info(f"Token kid: {kid}")
            logger.info(f"Available kids in JWKS: {[k['kid'] for k in jwks['keys']]}")

            # Find matching public key
            public_key = None
            for key in jwks['keys']:
                if key['kid'] == kid:
                    try:
                        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                        logger.info(f"Public key found for kid: {kid}")
                        break
                    except Exception as e:
                        logger.error(f'Failed to create public key from JWK: {str(e)}')
                        continue
            if not public_key:
                logger.error("No matching public key found after JWK processing")
                raise AuthenticationFailed('No matching public key found')
                
            # Decode and verify JWT
            payload = jwt.decode(
                token,
                public_key,
                algorithms=['RS256'],
                audience=[settings.KEYCLOAK_CLIENT_ID, 'account'],
                options={'verify_exp':True, 'verify_aud':True}
            )
            logger.info(f"JWT decoded successfully: {payload}")
            user = JWTUser(payload)  # Create custom user object
            return (user, token) # Return user object and token
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token error: {str(e)}")
            raise AuthenticationFailed(f'Invalid token: {str(e)}')
        except Exception as e:
            logger.error(f"Authentication error details: {str(e)}")
            raise AuthenticationFailed(f'Authentication error: {str(e)}')

# class CookieJWTAuthentication(BaseAuthentication):
#     def authenticate(self, request):
#         access_token = request.COOKIES.get('access_token')
#         # logger.info(f"Access token from cookie: {access_token}")
#         if not access_token:
#             logger.error("No access token found in cookies")
#             raise AuthenticationFailed('Authentication credentials were not provided.')
#         try:
#             token = AccessToken(access_token)
#             user_id = token['user_id']
#             logger.info(f"Authenticated user_id: {user_id}")
#             from django.contrib.auth.models import User
#             user = User.objects.get(id=user_id)
#             return (user, token)
#         except Exception as e:
#             logger.error(f"Token validation failed: {str(e)}")
#             raise AuthenticationFailed('Invalid token.')