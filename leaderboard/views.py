from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework import status
from rest_framework import mixins
from accounts.models import Player
import json


class LeaderBoardViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    @action(methods=['get'], detail=False)
    def all(self, request, *args, **kwargs):
        datas = []
        players = Player.objects.order_by('-rank')[:20]
        for player in players:
            data = {
                'rank': player.rank,
                'username': player.user.username,
                'score': player.score,
                'skill_rating': player.skill_rating
            }
            datas.append(data)
        return Response(datas, status=status.HTTP_200_OK)
