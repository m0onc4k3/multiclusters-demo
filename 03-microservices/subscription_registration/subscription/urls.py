from django.urls import path

from .views import SubscriptionFormView, SuccessView, LoginView

app_name = "subscription"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("subscription/", SubscriptionFormView.as_view(), name="subscription"),
    path("success/", SuccessView.as_view(), name="success"),
]
