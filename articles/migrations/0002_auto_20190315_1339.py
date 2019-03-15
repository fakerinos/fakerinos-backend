# Generated by Django 2.1.7 on 2019-03-15 13:39

from django.db import migrations, models
from django.contrib.auth import get_user_model


class Migration(migrations.Migration):
    dependencies = [
        ('articles', '0001_initial'),
    ]

    operations = [
        # domain
        migrations.AddField(
            'Article',
            'domain',
            models.URLField(null=True, blank=True),
        ),

        # published
        migrations.RenameField(
            'Article',
            'publish_date',
            'published'
        ),
        migrations.AlterField(
            'Article',
            'published',
            models.DateTimeField(null=True, blank=True),
        ),

        # created
        migrations.RenameField(
            'Article',
            'upload_date',
            'created'
        ),
        migrations.AlterField(
            'Article',
            'created',
            models.DateTimeField(auto_now_add=True),
        ),

        # modified
        migrations.AddField(
            'Article',
            'modified',
            models.DateTimeField(auto_now=True),
        ),

        # creator
        migrations.AddField(
            'Article',
            'creator',
            models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
        )
    ]
