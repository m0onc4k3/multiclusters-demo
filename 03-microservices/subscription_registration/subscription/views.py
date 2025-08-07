from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.http import JsonResponse
from django.views import View
from .forms import SubscriptionForm, LoginForm
from .models import Address
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
import requests

class LoginView(FormView):
    template_name = "subscription/login.html"
    form_class = LoginForm
    success_url = "/subscription/"

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            # Log in to Django session
            login(self.request, user)
            # Call API to set JWT cookies
            response = requests.post(
                'http://192.168.1.5:7000/api/v1/token/',
                json={'username': username, 'password': password}
            )
            if response.status_code == 200:
                # Forward cookies from API to client
                django_response = redirect(self.get_success_url())
                django_response.set_cookie(
                    key='access_token',
                    value=response.cookies.get('access_token'),
                    max_age=60 * 60,
                    httponly=True,
                    secure=False,  # Set to True in production
                    samesite='Strict',
                )
                django_response.set_cookie(
                    key='refresh_token',
                    value=response.cookies.get('refresh_token'),
                    max_age=24 * 60 * 60,
                    httponly=True,
                    secure=False,  # Set to True in production
                    samesite='Lax',
                )
                return django_response
            else:
                form.add_error(None, "Failed to obtain authentication token")
                return self.form_invalid(form)
        else:
            form.add_error(None, "Invalid username or password")
            return self.form_invalid(form)

class SubscriptionFormView(FormView):
    template_name = "subscription/subscription.html"
    form_class = SubscriptionForm
    success_url = "/success/"

    def form_valid(self, form):
        # Rely on JavaScript to call the API
        return super().form_valid(form)

class SuccessView(TemplateView):
    template_name = "subscription/success.html"

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