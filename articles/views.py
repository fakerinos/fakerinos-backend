from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from .models import Article, Deck, Tag
from .serializers import ArticleSerializer, DeckSerializer, TagSerializer
from rest_framework import permissions
from django.core import serializers
import json


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

    @action(detail=True, methods=['post'])
    def mark_finished(self, request, *args, **kwargs):
        deck = self.get_object()
        profile = request.user.profile
        profile.finished_decks.add(deck)
        profile.save()
        return Response(status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def star(self, request, *args, **kwargs):
        deck = self.get_object()
        profile = request.user.profile
        profile.starred_decks.add(deck)
        profile.save()
        return Response(status.HTTP_200_OK)

    @action(detail=True)
    def list_all_articles(self, request, pk):
        # pk in string
        data = []
        list = Deck.objects.get(pk=pk).articles.values_list('pk', flat=True)
        for i in list:
            data.append(i)
        return Response(json.dumps({"list_of_article_pk":data}), status=status.HTTP_200_OK)

    @action(detail=True)
    def all_articles(self, request, pk):
        # pk in string
        data = []
        list = Deck.objects.get(pk=pk).articles.all()
        # for i in list:
        #     data.append(ArticleSerializer(i))
        serializer = ArticleSerializer(list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.DjangoModelPermissions,)
    lookup_field = 'name'
