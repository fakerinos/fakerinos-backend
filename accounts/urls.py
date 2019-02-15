from django.urls import path, include
from allauth.account.views import confirm_email

urlpatterns = [
    path('', include('rest_auth.urls')),
    path('', include('allauth.urls')),
    path('register/account-confirm-email/<key>/', confirm_email),
    path('register/', include('rest_auth.registration.urls')),
]
