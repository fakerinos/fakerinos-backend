from django.urls import path, include
from rest_auth.views import LoginView, LogoutView, PasswordChangeView
from rest_auth.registration.views import RegisterView
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('user', views.UserViewSet)
router.register('profile', views.ProfileViewSet)
router.register('player', views.PlayerViewSet)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),
    path('', include(router.urls)),
]
