from django.shortcuts import render
from django.views import View
from .models import Article
from rest_framework.response import Response
from rest_framework import status


# Create your views here.
class ManageArticles(View):
    def post(self, request):
        return Response(status=status.HTTP_401_UNAUTHORIZED)
