from django.contrib import admin
from django.urls import path, include
from address_api.views import AddressListCreateAPIView, AddressDetailAPIView
#CookieTokenObtainPairView, CookieTokenRefreshView, 

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('', include('address_api.urls')),
    #path('api/v1/token/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    #path('api/v1/token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/addresses/', AddressListCreateAPIView.as_view(), name='address-list-create'),
    path('api/v1/addresses/<str:id>/', AddressDetailAPIView.as_view(), name='address-detail'),
]