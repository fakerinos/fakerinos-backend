from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<subject>', views.room, name='room'),
]
