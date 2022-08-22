from django.contrib import admin
from django.utils.translation import gettext_lazy as _


from .models import (
    Favorite, Ingredient, Recipe, RecipeIngredient,
    ShoppingCart, Tag
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'color')
    search_fields = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)


class RecipeIngredientsInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'in_favorites',
    )
    list_filter = ('name', 'author', 'tags',)
    inlines = (RecipeIngredientsInline,)

    @staticmethod
    @admin.display(description=_('Количество добавлений в избранное'))
    def in_favorites(obj):
        return obj.favorites.all().count()


class IdUserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
    )
    search_fields = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(IdUserAdmin):
    pass


@admin.register(Favorite)
class Favorite(IdUserAdmin):
    pass
