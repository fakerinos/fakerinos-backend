from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('article', views.ArticleViewSet)
router.register('articlebyurl', views.GetArticleByUrlViewSet)
router.register('deck', views.DeckViewSet)
router.register('tag', views.TagViewSet)
router.register('domain', views.DomainViewSet)
router.register('domaintag', views.DomainTagViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
