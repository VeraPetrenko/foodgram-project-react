from django.contrib import admin

from recipes.models import (
    Ingredient,
    IngredientRecipe,
    Recipe,
    Tag,
    TagRecipe,
    Follow,
    Favorite,
    ShoppingCart,
)


class IngredientRecipeInLine(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


class TagRecipeInLine(admin.TabularInline):
    model = TagRecipe
    extra = 1


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'following',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'tag',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientRecipeInLine, TagRecipeInLine,)
    list_display = (
        'id',
        'author',
        'name',
        'favorites_count',
    )
    list_filter = ('author', 'name', 'tags__name',)
    empty_value_display = '-пусто-'
    list_editable = (
        'author',
        'name',
    )

    @admin.display(description='Количество добавлений в избранное')
    def favorites_count(self, object):
        return Favorite.objects.filter(recipe=object).count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)
    empty_value_display = '-пусто-'
    list_editable = (
        'name',
        'measurement_unit',
    )


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)
