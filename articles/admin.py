from django.contrib import admin
from .models import Tag, Article, Deck, Domain, DomainTag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    pass


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    pass


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    pass


@admin.register(DomainTag)
class DomainTagAdmin(admin.ModelAdmin):
    pass
