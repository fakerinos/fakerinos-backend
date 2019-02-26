from django.urls import path, include
from .views import ManageArticles

urlpatterns = [
    path('', ManageArticles.as_view(), name='manage_articles')
]
