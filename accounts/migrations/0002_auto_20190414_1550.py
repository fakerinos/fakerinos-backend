# Generated by Django 2.1.7 on 2019-04-14 15:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('articles', '0001_initial'),
        ('rooms', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='room',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='players', to='rooms.Room'),
        ),
        migrations.AddField(
            model_name='player',
            name='starred_decks',
            field=models.ManyToManyField(blank=True, related_name='starrers', to='articles.Deck'),
        ),
    ]
