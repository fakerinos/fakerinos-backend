from django.apps import AppConfig


class ArticlesConfig(AppConfig):
    name = 'articles'

    def ready(self):
        super(ArticlesConfig, self).ready()
        from . import receivers
