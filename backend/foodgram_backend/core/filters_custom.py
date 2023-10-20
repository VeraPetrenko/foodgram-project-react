from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe, Ingredient


class FilterIngredient(FilterSet):
    """Фильтр для ингредиентов."""
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='startswith',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class FilterRecipe(FilterSet):
    """Фильтр для рецептов."""
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_is_favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_is_in_shopping_cart',
    )
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
    )
    author = filters.NumberFilter(
        field_name='author_id',
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'is_favorited',
            'is_in_shopping_cart',
            'tags',
        )

    def filter_is_favorited(self, queryset, field_name, value):
        if value:
            return queryset.filter(
                favorite_recipe__user=self.request.user
            )
        return queryset

    def filter_is_in_shopping_cart(self, queryset, field_name, value):
        if value:
            return queryset.filter(
                cart_recipe__user=self.request.user
            )
        return queryset
