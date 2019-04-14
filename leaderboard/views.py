from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework import status
from accounts.models import Player
from datetime import timedelta
import logging
import numpy as np


class LeaderBoardViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    @action(methods=['get'], detail=False)
    def all(self, request, *args, **kwargs):
        datas = self.get_player_rank_info()
        return Response(datas, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def day(self, request, *args, **kwargs):
        datas = self.get_player_rank_info(delta=timedelta(days=1))
        return Response(datas, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def week(self, request, *args, **kwargs):
        datas = self.get_player_rank_info(delta=timedelta(weeks=1))
        return Response(datas, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def month(self, request, *args, **kwargs):
        datas = self.get_player_rank_info(delta=timedelta(weeks=4))
        return Response(datas, status=status.HTTP_200_OK)

    def get_player_rank_info(self, players=None, delta=None, limit=10):
        datas = []
        queryset = (players or Player.objects.all())
        players = list(queryset)
        scores = np.array([player.get_score(delta=delta) for player in players])
        sort_indices = np.argsort(-scores)
        # TODO: Limit the number of players, somehow?
        for rank, i in enumerate(sort_indices):
            player = players[i]
            data = {
                'rank': rank + 1,
                'username': player.user.username,
                'score': scores[i],
                'skill_rating': player.skill_rating
            }
            datas.append(data)
        return datas
