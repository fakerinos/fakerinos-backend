# Generated by Django 2.1.7 on 2019-04-12 09:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0004_gameresults'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='deck',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, to='articles.Deck'),
        ),
        migrations.AlterField(
            model_name='room',
            name='tag',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='articles.Tag'),
        ),
    ]
