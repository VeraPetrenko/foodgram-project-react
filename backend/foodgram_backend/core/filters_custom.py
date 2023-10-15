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


class FilterRecipe(FilterSet):
    """Фильтр для рецептов."""
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='get_is_favorited',
    )
    # is_in_shopping_cart = filters.BooleanFilter(
    #     field_name='is_in_shopping_cart',
    #     method='get_is_in_shopping_cart',
    # )
#     # tags = filters.MultipleChoiceField()

    class Meta:
        model = Recipe
        fields = (
            # 'author',
            'is_favorited',
        #     'is_in_shopping_cart',
        #     'tags'
        )

    def get_is_favorited(self, queryset, field_name, value):
        if value:
            return queryset.filter(
                favorite_recipe__user=self.request.user
            )
        return queryset

    # def get_is_in_shopping_cart(self, queryset, field_name, value):
        