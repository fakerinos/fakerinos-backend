from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('top', views.TopLeaderBoardViewSet, basename='leaderboard-top')
router.register('relative', views.RelativeLeaderBoardViewSet, basename='leaderboard-relative')

urlpatterns = [
    path('', include(router.urls)),
]
