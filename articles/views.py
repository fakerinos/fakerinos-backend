from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required
from .models import Article
from .serializers import ArticleSerializer


class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer


class MostRecentArticles(APIView):
    def get(self, request):
        articles = Article.objects.order_by('upload_date')[:10]
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)


class EditArticles(APIView):
    @method_decorator(permission_required('articles.view_article', raise_exception=True))
    def get(self, request: Request):
        articles = Article.objects.filter(pk=request.query_params['id'])
        return Response(ArticleSerializer(articles, many=True).data, status=status.HTTP_200_OK)

    @method_decorator(permission_required('articles.add_article', raise_exception=True))
    def post(self, request: Request):
        serializer = ArticleSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(permission_required('articles.change_article', raise_exception=True))
    def patch(self, request: Request):
        serializer = ArticleSerializer()
        return Response(status=status.HTTP_200_OK)

    @method_decorator(permission_required('articles.delete_article', raise_exception=True))
    def delete(self, request: Request):
        pass
