from django.db import models
from django.contrib.auth import get_user_model
from fakerinos.models import BaseModel
from rooms.models import Room
from articles.models import Tag

User = get_user_model()


class Profile(BaseModel):
    EDUCATION_CHOICES = (
        ('X', "Unknown"),
        ('KG', "Kindergarten"),
        ('PR', "Primary"),
        ('SE', "Secondary"),
        ('UG', "Undergraduate"),
        ('PG', "Postgraduate"),
        ('PH', "Doctorate"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, editable=False, related_name='profile')
    interests = models.ManyToManyField(Tag, related_name='interested_users')
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='players', editable=False, null=True)
    education = models.CharField(max_length=2, choices=EDUCATION_CHOICES, default='SE')
    complete = models.BooleanField(editable=False, default=False)


def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


models.signals.post_save.connect(create_profile, sender=User)
