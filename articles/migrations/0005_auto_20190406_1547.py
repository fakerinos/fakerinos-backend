# Generated by Django 2.1.7 on 2019-04-06 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0004_deck_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]