# Generated by Django 2.1.7 on 2019-04-13 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0008_gameresult_game_uid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='max_players',
            field=models.IntegerField(default=2, editable=False),
        ),
    ]