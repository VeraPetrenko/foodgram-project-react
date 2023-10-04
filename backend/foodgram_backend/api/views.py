from django.shortcuts import HttpResponse
from djoser.views import UserViewSet
from django_filters import rest_framework as filters
from rest_framework.viewsets import ModelViewSet
from recipes.models import Recipe, Tag, Ingredient
from api.serializers import TagSerializer, RecipeSerializer, RecipeCreateSerializer, IngredientSerializer
from core import filters_custom


class CustomUserViewSet(UserViewSet):
    pass


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    pagination_class = None
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = filters_custom.FilterIngredient


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    # def dispatch(self, request, *args, **kwargs):
    #     # добавить какой-нибудь принт, если что-то пойдет не так
    #     # либо удалить
    #     return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # с помощью prefetch_related сократили кол-во запросов
        # к БД при отображении списка рецептов
        recipes = Recipe.objects.prefetch_related(
            'ingredient_recipe__ingredient', 'tags'
        ).all()
        return recipes

    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
