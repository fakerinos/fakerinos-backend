from django.contrib import admin
from .models import BaseModel, CreatorModel


@admin.register(BaseModel)
class BaseModelAdmin(admin.ModelAdmin):
    pass


@admin.register(CreatorModel)
class CreatorModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if change:
            obj.modifier = request.user
        else:
            obj.creator = request.user
        obj.save()
