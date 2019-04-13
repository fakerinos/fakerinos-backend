from django.contrib import admin
from .models import Room, GameResult


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    pass


@admin.register(GameResult)
class GameResultAdmin(admin.ModelAdmin):
    pass
