from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
import logging

logger = logging.getLogger(__name__)

class CookieJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get('access_token')
        # logger.info(f"Access token from cookie: {access_token}")
        if not access_token:
            logger.error("No access token found in cookies")
            raise AuthenticationFailed('Authentication credentials were not provided.')
        try:
            token = AccessToken(access_token)
            user_id = token['user_id']
            logger.info(f"Authenticated user_id: {user_id}")
            from django.contrib.auth.models import User
            user = User.objects.get(id=user_id)
            return (user, token)
        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}")
            raise AuthenticationFailed('Invalid token.')