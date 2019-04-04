from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime
from rooms.models import Room
from articles.models import Tag, Deck


class User(AbstractUser):
    pass


class Player(models.Model):
    user = models.OneToOneField(User, primary_key=True, editable=False, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='players', editable=False, null=True)
    hosted_room = models.OneToOneField(Room, on_delete=models.SET_NULL, related_name='host', editable=False, null=True)
    skill_rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(1000)],
                                       editable=False,
                                       default=500)


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

    GENDER_UNKNOWN = 0
    GENDER_MALE = 1
    GENDER_FEMALE = 2
    GENDER_NON_BINARY = 3
    GENDER_SECRET = 4
    GENDER_CHOICES = (
        (GENDER_UNKNOWN, "Unknown"),
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
        (GENDER_NON_BINARY, "Non-binary"),
        (GENDER_SECRET, "Secret"),
    )

    user = models.OneToOneField(User, primary_key=True, editable=False, on_delete=models.CASCADE)
    education = models.PositiveSmallIntegerField(choices=EDUCATION_CHOICES, default=EDUCATION_UNKNOWN, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.PositiveSmallIntegerField(choices=GENDER_CHOICES, default=GENDER_UNKNOWN, blank=True)
    name = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    interests = models.ManyToManyField(Tag, related_name='interested_users')
    starred_decks = models.ManyToManyField(Deck, related_name='starrers')
    onboarded = models.BooleanField(default=False, blank=True)

    @property
    def is_complete(self):
        conditions = [
            self.education != self.EDUCATION_UNKNOWN,
            len(self.interests.all()),
            self.birth_date is not None,
            self.gender != self.GENDER_UNKNOWN,
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
    return user_model(username='Anonymous', )
