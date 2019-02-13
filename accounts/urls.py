from django.urls import path, include

urlpatterns = [
    path('', include('rest_auth.urls')),
    path('', include('allauth.urls')),
    path('register/', include('rest_auth.registration.urls')),
]
