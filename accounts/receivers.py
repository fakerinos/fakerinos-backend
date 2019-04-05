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
from guardian import shortcuts
import logging

User = get_user_model()


# TODO: Do a better validation of the provided user permission names
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
        profile = Profile.objects.create(user=instance)
        model_name = profile._meta.model_name
        perms = Permission.objects.filter(content_type__model=model_name)
        assert perms.exists(), 'no perms for {}'.format(model_name)
        for perm in perms:
            shortcuts.assign_perm(perm, instance, obj=profile)


@receiver(models.signals.post_save, sender=User)
def create_player(sender, instance, created, **kwargs):
    if created:
        logging.info("Creating Player for User {}".format(instance.pk))
        player = Player.objects.create(user=instance)
        model_name = player._meta.model_name
        perms = Permission.objects.filter(content_type__model=model_name)
        assert perms.exists(), 'no perms for {}'.format(model_name)
        for perm in perms:
            shortcuts.assign_perm(perm, instance, obj=player)
