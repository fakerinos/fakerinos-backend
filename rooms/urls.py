from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('single-player', views.SinglePlayer, 'single-player')
router.register('games', views.GameResultViewSet, 'games')

urlpatterns = [
    path('', include(router.urls)),
]
