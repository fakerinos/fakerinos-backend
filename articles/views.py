from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from .models import Article
from .serializers import ArticleSerializer


class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (permissions.IsAuthenticated, permissions.DjangoModelPermissions)
