from django.urls import path
from .views import AddressListCreateAPIView, AddressDetailAPIView

urlpatterns = [
    path('api/v1/addresses/', AddressListCreateAPIView.as_view(), name='address-list-create'),
    path('api/v1/addresses/<str:id>/', AddressDetailAPIView.as_view(), name='address-detail'),
]