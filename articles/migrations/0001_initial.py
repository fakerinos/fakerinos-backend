# Generated by Django 2.1.7 on 2019-04-05 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('headline', models.CharField(max_length=500)),
                ('rating', models.CharField(max_length=50)),
                ('domain', models.URLField(blank=True)),
                ('text', models.TextField(blank=True)),
                ('thumbnail_url', models.URLField(blank=True, max_length=500)),
                ('author', models.CharField(blank=True, max_length=100)),
                ('explanation', models.TextField(blank=True)),
                ('published', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Deck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=50)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('thumbnail_url', models.URLField(blank=True, max_length=500)),
                ('articles', models.ManyToManyField(related_name='decks', to='articles.Article')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='article',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='articles', to='articles.Tag'),
        ),
    ]
