from django.urls import path, include
from .views import GetMostRecentArticles

urlpatterns = [
    path('recent', GetMostRecentArticles.as_view(), name='recent_articles')
]
