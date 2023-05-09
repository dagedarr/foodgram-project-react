from django.contrib import admin

from .models import Ingredient, Component, Recipe, Tag, ShoppingCart, Favorite


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)


class ComponentsInline(admin.TabularInline):
    """Класс для добавления компонентов при создании рецептов через админку."""
    model = Component


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'name', 'text', 'cooking_time',)
    inlines = (ComponentsInline,)


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug',)


class ComponentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount',)


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
