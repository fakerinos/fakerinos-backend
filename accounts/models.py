from django.db import models
from django.contrib.auth.models import AbstractUser
from rooms.models import Room
from articles.models import Tag


class User(AbstractUser):
    pass


class Player(models.Model):
    user = models.OneToOneField(User, primary_key=True, editable=False, on_delete=models.CASCADE)
    score = models.IntegerField(default=0, editable=False)
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='players', editable=False, null=True)
    hosted_room = models.OneToOneField(Room, on_delete=models.SET_NULL, related_name='host', editable=False, null=True)


class Profile(models.Model):
    EDUCATION_UNKNOWN = 0
    EDUCATION_KINDERGARTEN = 1
    EDUCATION_PRIMARY = 2
    EDUCATION_SECONDARY = 3
    EDUCATION_UNDERGRADUATE = 4
    EDUCATION_POSTGRADUATE = 5
    EDUCATION_DOCTORATE = 6
    EDUCATION_CHOICES = (
        (EDUCATION_UNKNOWN, "Unknown"),
        (EDUCATION_KINDERGARTEN, "Kindergarten"),
        (EDUCATION_PRIMARY, "Primary"),
        (EDUCATION_SECONDARY, "Secondary"),
        (EDUCATION_UNDERGRADUATE, "Undergraduate"),
        (EDUCATION_POSTGRADUATE, "Postgraduate"),
        (EDUCATION_DOCTORATE, "Doctorate"),
    )

    user = models.OneToOneField(User, primary_key=True, editable=False, on_delete=models.CASCADE)
    interests = models.ManyToManyField(Tag, related_name='interested_users')
    education = models.PositiveSmallIntegerField(choices=EDUCATION_CHOICES, default=EDUCATION_UNKNOWN)

    @property
    def is_complete(self):
        conditions = [
            self.education != self.EDUCATION_UNKNOWN,
            len(self.interests.all()),
        ]
        return all(conditions)


def get_anonymous_user_instance(user_model) -> User:
    """
    Used by Django-guardian during migrations.
    Should return a User instance
    """
    return user_model(username='Anonymous', )
