from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('articles', views.ArticleViewSet)
router.register('decks', views.DeckViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
