from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('articles', views.ArticleViewSet)
router.register('decks', views.DeckViewSet)
router.register('', views.ArticleViewSet, 'articles')

urlpatterns = [
    path('', include(router.urls)),
]
