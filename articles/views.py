from rest_framework.viewsets import mixins, ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from .models import Article, Deck, Tag
from .serializers import ArticleSerializer, DeckSerializer, TagSerializer
from rooms.signals import article_swiped
from rest_framework import permissions
from random import shuffle


class GetArticleByUrlViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    """
    Get an article by looking up its URL.
    URL must have all '/' substituted for '_'.
    """
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = 'url_hash'


class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (permissions.DjangoModelPermissions,)

    def get_permissions(self):
        if self.action and 'swipe' in self.action:
            return [permissions.IsAuthenticated()]
        return [permissions.DjangoModelPermissions()]

    @action(methods=['post'], detail=True)
    def swipe_true(self, request, *args, **kwargs):
        article_swiped.send(self.__class__, player=request.user.player, article=self.get_object(), outcome=True)
        return Response(status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def swipe_false(self, request, *args, **kwargs):
        article_swiped.send(self.__class__, player=request.user.player, article=self.get_object(), outcome=False)
        return Response(status=status.HTTP_200_OK)


class DeckViewSet(ModelViewSet):
    queryset = Deck.objects.all()
    serializer_class = DeckSerializer
    permission_classes = (permissions.DjangoModelPermissions,)

    @action(detail=False, methods=['get'])
    def recommended(self, request):
        decks = self.get_recommended_decks(request.user)
        serializer = self.get_serializer(decks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_recommended_decks(self, user):
        tags = user.profile.interests.all()
        tagged_decks = Deck.objects.filter(tags__in=tags).distinct()[:10]
        return tagged_decks

    @action(detail=False, methods=['get'])
    def trending(self, request):
        decks = self.get_trending_decks(request.user)
        serializer = self.get_serializer(decks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_trending_decks(self, request):
        decks = list(Deck.objects.all())
        shuffle(decks)
        return decks[:3]

    @action(detail=False, methods=['get'])
    def poll(self, request):
        poll_articles = Article.objects.filter(is_poll=True)
        true_swiped = request.user.player.true_swiped.all()
        false_swiped = request.user.player.false_swiped.all()
        seen_articles = true_swiped | false_swiped
        unseen_poll_articles = poll_articles.difference(seen_articles)[:5]
        if not unseen_poll_articles.count():
            raise NotFound("No new poll articles.")
        deck = Deck.objects.create(title="Current Affairs")
        deck.articles.set(unseen_poll_articles)
        data = DeckSerializer([deck], many=True).data
        deck.delete()
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def mark_finished(self, request, *args, **kwargs):
        deck = self.get_object()
        player = request.user.player
        player.finished_decks.add(deck)
        player.save()
        return Response({'message': 'DEPRECATED'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def star(self, request, *args, **kwargs):
        deck = self.get_object()
        player = request.user.player
        if deck in player.starred_decks.all():
            player.starred_decks.remove(deck)
        else:
            player.starred_decks.add(deck)
        player.save()
        return Response(status.HTTP_200_OK)

    @action(detail=True)
    def articles(self, request, *args, **kwargs):
        deck = self.get_object()
        articles = deck.articles.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.DjangoModelPermissions,)
    lookup_field = 'name'
