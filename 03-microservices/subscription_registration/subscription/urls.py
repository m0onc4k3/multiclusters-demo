from django.urls import path

from .views import SubscriptionFormView, SuccessView, OIDCLoginView, OIDCCallbackView
#LoginView

app_name = "subscription"

urlpatterns = [
    # path("login/", LoginView.as_view(), name="login"),
    path('login/', OIDCLoginView.as_view(), name='login'),
    path('oidc/callback/', OIDCCallbackView.as_view(), name='oidc_callback'),
    path("subscription/", SubscriptionFormView.as_view(), name="subscription"),
    path("success/", SuccessView.as_view(), name="success"),
]
