from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from .models import Article, Deck
from .serializers import ArticleSerializer, DeckSerializer


class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (permissions.IsAuthenticated, permissions.DjangoModelPermissions)


class DeckViewSet(ModelViewSet):
    queryset = Deck.objects.all()
    serializer_class = DeckSerializer

