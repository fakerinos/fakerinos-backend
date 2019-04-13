# Generated by Django 2.1.7 on 2019-04-12 07:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0008_auto_20190407_1256'),
        ('rooms', '0002_room_subject'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='deck',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='articles.Deck'),
        ),
        migrations.AddField(
            model_name='room',
            name='tag',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, to='articles.Tag'),
        ),
        migrations.AlterField(
            model_name='room',
            name='status',
            field=models.CharField(blank=True, default='NEW', editable=False, max_length=128),
        ),
        migrations.AlterField(
            model_name='room',
            name='subject',
            field=models.CharField(blank=True, editable=False, max_length=50, null=True, unique=True),
        ),
    ]
