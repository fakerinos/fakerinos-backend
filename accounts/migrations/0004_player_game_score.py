# Generated by Django 2.1.7 on 2019-04-20 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20190416_1414'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='game_score',
            field=models.IntegerField(default=0),
        ),
    ]
