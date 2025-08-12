from django.urls import path
from .views import AddressListCreateAPIView, AddressDetailAPIView, CookieTokenObtainPairView

urlpatterns = [
    path('api/v1/token/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/addresses/', AddressListCreateAPIView.as_view(), name='address-list-create'),
    path('api/v1/addresses/<str:id>/', AddressDetailAPIView.as_view(), name='address-detail'),
]