from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('', views.ArticleViewSet, 'articles')

urlpatterns = [
    # path('', views.EditArticles.as_view(), name='articles'),
    path('', include(router.urls)),
    path('recent', views.MostRecentArticles.as_view(), name='recent_articles'),
]
