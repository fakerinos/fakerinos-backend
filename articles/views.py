from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions, status
from .models import Article, Deck
from .serializers import ArticleSerializer, DeckSerializer


class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    # permission_classes = (permissions.IsAuthenticated, permissions.DjangoModelPermissions)


class DeckViewSet(ModelViewSet):
    # Define queryset && Serializer
    queryset = Deck.objects.all()
    serializer_class = DeckSerializer


    # get specific deck
    @action(detail=True)
    def specifically(self, request, subject=None):
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            return Response({'status': 'now get article'})
        else:
            return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
