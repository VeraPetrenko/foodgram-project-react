from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe, Tag, Ingredient


class FilterIngredient(FilterSet):
    """Фильтр для ингредиентов."""
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='startswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


# class FilterRecipe(FilterSet):
#     """Фильтр для рецептов."""
#     # is_favorited is_in_shopping_cart= filters.BooleanFilter(
#     #     field_name='',
#     # )
#     # tags = filters.MultipleChoiceField()
#     # author = 

#     class Meta:
#         model = Recipe
#         fields = (
#             'author',
#             'is_favorited',
#             'is_in_shopping_cart',
#             'tags'
#         )