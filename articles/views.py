from rest_framework.viewsets import ModelViewSet
from .models import Article, Deck, Tag
from .serializers import ArticleSerializer, DeckSerializer, TagSerializer
from rest_framework import permissions


class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)


class DeckViewSet(ModelViewSet):
    queryset = Deck.objects.all()
    serializer_class = DeckSerializer
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    lookup_field = 'name'
