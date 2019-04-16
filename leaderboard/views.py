from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework import status
from accounts.models import Player
from accounts.serializers import ProfileSerializer
from .models import LeaderBoardStaleMarker
from datetime import timedelta
import logging
import numpy as np

eps = 0.000001
PLAYER_RANKS_CACHE = {}


def get_all_player_ranks(delta=None, use_cache=True):
    """
    Get rank and score information for all players in the database.
    Args:
        delta:
        use_cache: Whether to retrieve cached results

    Returns:

    """
    fresh_indicator, created = LeaderBoardStaleMarker.objects.get_or_create(delta=delta)
    if fresh_indicator.fresh and not created and use_cache and delta in PLAYER_RANKS_CACHE:
        return PLAYER_RANKS_CACHE[delta]
    players = list(Player.objects.all())
    scores = np.array([player.get_score(delta=delta) for player in players])
    sort_indices = np.argsort(-scores)
    rank_to_player = {rank + 1: players[i] for rank, i in enumerate(sort_indices)}
    player_pk_to_rank = {players[i].pk: rank + 1 for rank, i in enumerate(sort_indices)}
    rank_to_score = {rank + 1: scores[i] for rank, i in enumerate(sort_indices)}
    output = (rank_to_player, player_pk_to_rank, rank_to_score)
    PLAYER_RANKS_CACHE[delta] = output
    fresh_indicator.fresh = True
    fresh_indicator.save()
    return output


def get_player_rank_info(request, delta=None, count=10, relative=False, target_player=None):
    """
    Get verbose rank information for players in rank range.

    Args:
        request: Request object from view. Required for serializer context.
        delta: Time delta (backwards from the current moment) to start counting scores from
        count: The number of player records to return
        relative:
        target_player: The central player to get records relative to

    Returns:
        list:
    """
    rank_info = []
    rank_to_player, player_pk_to_rank, rank_to_score = get_all_player_ranks(delta=delta)
    ranks = sorted(list(rank_to_player.keys()))
    if relative:
        # Target behavior is to return (count // 2) above and (count // 2 - 1) below
        assert target_player is not None
        player_rank = player_pk_to_rank[target_player.pk]
        rank_index = ranks.index(player_rank)
        target_below = int(round(count / 2 + eps))
        target_above = int(round(count / 2 + eps)) - (count % 2)
        below = rank_index
        above = len(ranks) - rank_index
        if above < target_above:
            target_below += target_above - above
        elif below < target_below:
            target_above += target_below - below
        ranks = ranks[max(0, rank_index - target_below):max(0, rank_index + target_above)]
    else:
        ranks = ranks[:count]
    for rank in ranks:
        player = rank_to_player[rank]
        profile = player.user.profile
        data = {
            'rank': rank,
            'profile': ProfileSerializer(profile, context={'request': request}).data,
            'username': player.user.username,
            'score': rank_to_score[rank],
            'skill_rating': player.skill_rating
        }
        rank_info.append(data)
    return rank_info


class TopLeaderBoardViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    @action(methods=['get'], detail=False)
    def all(self, request, *args, **kwargs):
        datas = get_player_rank_info(request, )
        return Response(datas, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def day(self, request, *args, **kwargs):
        datas = get_player_rank_info(request, delta=timedelta(days=1))
        return Response(datas, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def week(self, request, *args, **kwargs):
        datas = get_player_rank_info(request, delta=timedelta(weeks=1))
        return Response(datas, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def month(self, request, *args, **kwargs):
        datas = get_player_rank_info(request, delta=timedelta(weeks=4))
        return Response(datas, status=status.HTTP_200_OK)


class RelativeLeaderBoardViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    @action(methods=['get'], detail=False)
    def all(self, request, *args, **kwargs):
        datas = get_player_rank_info(request, relative=True, target_player=request.user.player)
        return Response(datas, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def day(self, request, *args, **kwargs):
        datas = get_player_rank_info(request, delta=timedelta(days=1), relative=True, target_player=request.user.player)
        return Response(datas, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def week(self, request, *args, **kwargs):
        datas = get_player_rank_info(request, delta=timedelta(weeks=1), relative=True,
                                     target_player=request.user.player)
        return Response(datas, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def month(self, request, *args, **kwargs):
        datas = get_player_rank_info(request, delta=timedelta(weeks=4), relative=True,
                                     target_player=request.user.player)
        return Response(datas, status=status.HTTP_200_OK)
