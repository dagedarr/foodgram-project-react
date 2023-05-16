from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import Component, Favorite, Ingredient, Recipe, ShoppingCart, Tag


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)


class ComponentsInline(admin.TabularInline):
    """Класс для добавления компонентов при создании рецептов через админку."""
    model = Component
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'name', 'text',
                    'cooking_time', 'favorite_count')
    inlines = (ComponentsInline,)
    search_fields = ('name', 'author__username', 'tags__name')
    list_filter = ('pub_date', 'author', 'name', 'tags')
    filter_horizontal = ('ingredients',)

    def favorite_count(self, obj):
        return obj.favorite.count()

    favorite_count.short_description = 'Количество подписок'


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug',)
    list_filter = ('name',)
    search_fields = ('name',)


class ComponentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount',)
    list_filter = ('recipe', 'ingredient')
    search_fields = ('name',)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user',)
    search_fields = ('user',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user',)
    search_fields = ('user',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Component, ComponentsAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
