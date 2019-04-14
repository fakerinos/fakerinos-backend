from django.dispatch import Signal

game_started = Signal(providing_args=['room', 'deck'])
game_ended = Signal(providing_args=['room', 'deck', 'player_scores'])
player_joined_room = Signal(providing_args=['room', 'player'])
player_left_room = Signal(['room', 'player'])
