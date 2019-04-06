from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from .models import Article, Deck, Tag
from .serializers import ArticleSerializer, DeckSerializer, TagSerializer
from rest_framework import permissions


class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (permissions.DjangoModelPermissions,)


class DeckViewSet(ModelViewSet):
    queryset = Deck.objects.all()
    serializer_class = DeckSerializer
    permission_classes = (permissions.DjangoModelPermissions,)

    @action(detail=False)
    def recommended(self, request):
        decks = self.get_recommended_decks(request)
        serializer = self.get_serializer(decks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_recommended_decks(self, request):
        user = request.user
        tags = user.profile.interests.all()
        tagged_decks = Deck.objects.filter(tags__in=tags).distinct()[:10]
        return tagged_decks


class RecommendedDecksViewSet(generics.ListAPIView):
    serializer_class = DeckSerializer
    permission_classes = (permissions.DjangoModelPermissions,)

    def get_queryset(self):
        user = self.request.user
        tags = user.profile.interests.all()
        tagged_decks = Deck.objects.filter(tags__in=tags).distinct()[:10]
        return tagged_decks


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.DjangoModelPermissions,)
    lookup_field = 'name'
