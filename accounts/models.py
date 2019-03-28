from django.db import models
from django.contrib.auth.models import AbstractUser
from rooms.models import Room
from articles.models import Tag


class User(AbstractUser):
    EDUCATION_CHOICES = (
        ('X', "Unknown"),
        ('KG', "Kindergarten"),
        ('PR', "Primary"),
        ('SE', "Secondary"),
        ('UG', "Undergraduate"),
        ('PG', "Postgraduate"),
        ('PH', "Doctorate"),
    )
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='players', editable=False, null=True)
    hosted_room = models.OneToOneField(Room, on_delete=models.SET_NULL, related_name='host', editable=False, null=True)
    complete = models.BooleanField(editable=False, default=False)
    interests = models.ManyToManyField(Tag, related_name='interested_users')
    education = models.CharField(max_length=2, choices=EDUCATION_CHOICES, default='SE')


def get_anonymous_user_instance(user_model):
    return user_model(username='Anonymous', )
