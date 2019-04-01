from ..models import BaseModel
from django.test import TestCase


class TestBaseModel(TestCase):
    class ConcreteModel(BaseModel):
        pass

    def test_create_model(self):
        instance = self.ConcreteModel.objects.create()
        self.assertTrue(self.ConcreteModel.objects.filter(pk=instance.pk).exists())

    def test_delete_model(self):
        instance = self.ConcreteModel.objects.create()
        instance.delete()
        self.assertFalse(self.ConcreteModel.objects.filter(pk=instance.pk).exists())

    def test_modified_time(self):
        instance = self.ConcreteModel.objects.create()
        initial_modified = instance.modified
        instance.save()
        new_modified = instance.modified
        self.assertNotEqual(initial_modified, new_modified)
