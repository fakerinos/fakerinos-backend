# Generated by Django 2.1.7 on 2019-04-20 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0004_auto_20190419_0908'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='url_hash',
            field=models.CharField(blank=True, editable=False, max_length=1000),
        ),
    ]