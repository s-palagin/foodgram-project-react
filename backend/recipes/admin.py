from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient, Tag


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'color')
    search_fields = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)


class RecipeIngredientsInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
    )
    list_filter = ('name', 'author', 'tags',)
    inlines = (RecipeIngredientsInline,)


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
