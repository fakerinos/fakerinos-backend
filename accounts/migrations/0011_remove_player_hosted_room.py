# Generated by Django 2.1.7 on 2019-04-12 09:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_auto_20190412_0755'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='hosted_room',
        ),
    ]
