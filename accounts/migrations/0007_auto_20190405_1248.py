# Generated by Django 2.1.7 on 2019-04-05 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_profile_onboarded'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='education',
            field=models.CharField(blank=True, default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='profile',
            name='gender',
            field=models.CharField(blank=True, default='Unknown', max_length=50),
        ),
    ]
