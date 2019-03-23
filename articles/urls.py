from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('decks', views.DeckViewSet)
router.register('articles', views.ArticleViewSet, 'articles')

urlpatterns = [
    path('', include(router.urls)),
]
