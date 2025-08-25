from django.contrib import admin
from django.urls import include, path
#from subscription.views import SubscriptionFormView, SuccessView
#, HealthCheckView

app_name = "subscription"

urlpatterns = [
    #path("admin/", admin.site.urls),
    path("", include("subscription.urls")),
    #path("subscription/", SubscriptionFormView.as_view(), name="subscription"),
    #path("success/", SuccessView.as_view(), name="success"),
    #path("health/", HealthCheckView.as_view(), name="health"),  # Add this line
]
