# Generated by Django 2.1.7 on 2019-04-12 08:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('articles', '0008_auto_20190407_1256'),
    ]

    operations = [
        migrations.RenameField(model_name='deck', old_name='subject', new_name='title'),
        migrations.AlterField(
            model_name='deck',
            name='title',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]