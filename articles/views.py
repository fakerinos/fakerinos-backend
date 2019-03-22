from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions, status
from django_filters.rest_framework import DjangoFilterBackend
from .models import Article, Deck
from .serializers import ArticleSerializer, DeckSerializer


class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (permissions.IsAuthenticated, permissions.DjangoModelPermissions)


class DeckViewSet(ModelViewSet):
    # Define queryset && Serializer
    queryset = Deck.objects.all()
    serializer_class = DeckSerializer

    # get specific deck
    @action(detail=False)
    def name(self, request, subject, pk=None):
        filter_backend = (DjangoFilterBackend,)
        filter_fields = ('subject')
        lookup_field = "deck__subject"
        #
        # if subject != None:
        #     if self.queryset.filter(subject=subject).exists():
        #         return self.queryset.get(subject=subject)
        #     else:
        #         return Response({'status': 'no such article'})

    # randomly get articles

