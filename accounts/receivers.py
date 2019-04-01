"""
Defines signal receivers for this app.
This module should only be imported once models are loaded and ready for use,
such as in the `ready` method of the app's AppConfig.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db import models
from django.dispatch import receiver
from django.conf import settings
from functools import lru_cache
from .models import Player, Profile
import logging

User = get_user_model()


# TODO: Do a better validation of the provided user permission names
# @lru_cache(maxsize=4)
def get_default_permissions(permission_names=settings.DEFAULT_USER_PERMISSIONS):
    permissions = list(Permission.objects.filter(codename__in=permission_names))
    if len(permissions) != len(permission_names):
        raise ValueError("Could not find some Permission(s). Verify DEFAULT_USER_PERMISSIONS in your settings.")
    return permissions


@receiver(models.signals.post_save, sender=User)
def assign_default_user_group(sender, instance, created, **kwargs):
    if created:
        group, group_created = Group.objects.get_or_create(name='default')
        try:
            logging.info("Adding User {} to Group '{}'...".format(instance.pk, group.name))
            if group_created:
                logging.info("Assigning default Permissions to Group '{}'".format(group.name))
                permissions = get_default_permissions()
                for perm in permissions:
                    group.permissions.add(perm)
                group.save()
            instance.groups.add(group)
        except Exception as e:
            logging.error("Failed to assign default Permissions.")
            group.delete()
            raise


@receiver(models.signals.post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        logging.info("Creating Profile for User {}".format(instance.pk))
        Profile.objects.create(user=instance)


@receiver(models.signals.post_save, sender=User)
def create_player(sender, instance, created, **kwargs):
    if created:
        logging.info("Creating Player for User {}".format(instance.pk))
        Player.objects.create(user=instance)
