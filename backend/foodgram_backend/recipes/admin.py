from django.contrib import admin

from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag, TagRecipe, Follow


class IngredientRecipeInLine(admin.TabularInline):
    model = IngredientRecipe
    # 1 доп кнопка для создания:
    extra = 1


class TagRecipeInLine(admin.TabularInline):
    model = TagRecipe
    # 1 доп кнопка для создания:
    extra = 2


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientRecipeInLine, TagRecipeInLine,)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass
