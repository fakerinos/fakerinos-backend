from django.db import models
from django.contrib.auth import get_user_model


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CreatorModel(BaseModel):
    creator = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        related_name='%(class)s_creator',
        editable=False,
        null=True
    )
    modifier = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        related_name='%(class)s_modifier',
        editable=False,
        null=True
    )

    class Meta:
        abstract = True
