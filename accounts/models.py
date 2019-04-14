from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime
from guardian.mixins import GuardianUserMixin
from django.conf import settings
from articles.models import Tag, Deck


class User(GuardianUserMixin, AbstractUser):
    pass


class Player(models.Model):
    user = models.OneToOneField(User, primary_key=True, editable=False, on_delete=models.CASCADE)
    room = models.ForeignKey('rooms.Room', on_delete=models.SET_NULL, related_name='players', editable=False, null=True,
                             blank=True)
    skill_rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(1000)],
                                       editable=False,
                                       default=500)
    score = models.IntegerField(default=0)
    ready = models.BooleanField(default=False)


class Profile(models.Model):
    user = models.OneToOneField(User, primary_key=True, editable=False, on_delete=models.CASCADE)
    education = models.CharField(max_length=50, default="Unknown", blank=True)
    gender = models.CharField(max_length=50, default="Unknown", blank=True)
    birth_date = models.DateField(null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    interests = models.ManyToManyField(Tag, related_name='interested_users', blank=True)
    starred_decks = models.ManyToManyField(Deck, related_name='starrers', blank=True)
    onboarded = models.BooleanField(default=False, blank=True)
    finished_decks = models.ManyToManyField(Deck, related_name='finishers', blank=True)

    @property
    def is_complete(self):
        conditions = [
            self.education != "Unknown",
            len(self.interests.all()),
            self.birth_date is not None,
            self.gender != "Unknown",
            self.avatar is not None,
            self.name,
        ]
        return all(conditions)

    @property
    def age(self):
        if self.birth_date is not None:
            return (datetime.now().date() - self.birth_date).days // 365


def get_anonymous_user_instance(user_model) -> User:
    """
    Used by Django-guardian during migrations.
    Should return a User instance
    """
    return user_model(username=settings.ANONYMOUS_USER_NAME, )
