from django.views import View
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from .models import Article
from .serializers import ArticleSerializer


# Create your views here.
class GetMostRecentArticles(View):
    @csrf_exempt
    def get(self, request):
        articles = Article.objects.order_by('upload_date')[:10]
        serializer = ArticleSerializer(articles, many=True)
        return JsonResponse(serializer.data, safe=False)

