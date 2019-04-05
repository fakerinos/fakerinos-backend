from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, Player


@admin.register(User)
class UserAdmin(UserAdmin):
    pass


@admin.register(Player)
class PlayerAdmin(GuardedModelAdmin):
    pass


@admin.register(Profile)
class ProfileAdmin(GuardedModelAdmin):
    pass
