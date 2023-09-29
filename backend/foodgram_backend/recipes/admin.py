from django.contrib import admin

from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag


class IngredientRecipeInLine(admin.TabularInline):
    model = IngredientRecipe
    # 1 доп кнопка для создания:
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientRecipeInLine,)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass