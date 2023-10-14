from django.shortcuts import HttpResponse
from djoser.views import UserViewSet
from django_filters import rest_framework as filters
from rest_framework.viewsets import ModelViewSet
from recipes.models import Recipe, Tag, Ingredient, Follow, Favorite
from api.serializers import (
    TagSerializer,
    RecipeSerializer,
    RecipeCreateSerializer,
    IngredientSerializer,
    FollowSerializer,
    FollowCreateDeleteSerializer,
    UserSerializer,
    UserCreateSerializer,
    FavoriteCreateDeleteSerializer,
)
from core import filters_custom
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


User = get_user_model()


class CustomUserViewSet(UserViewSet):

    @action(["get"], detail=False)
    def me(self, request):
        user = get_object_or_404(User, id=request.user.id)
        serializer = UserSerializer(user)
        # пермишн будет только авторизованный
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer


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

    def get_queryset(self):
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


class FollowViewSet(ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )

    def delete(self, request, *args, **kwargs):
        following = get_object_or_404(
            User,
            pk=kwargs['following_id']
        )
        instance = get_object_or_404(
            Follow,
            user=request.user,
            following=following)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'destroy':
            return FollowCreateDeleteSerializer
        return FollowSerializer


class FollowListViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = FollowSerializer

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)


class FavoriteViewSet(ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteCreateDeleteSerializer

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )

    def delete(self, request, *args, **kwargs):
        fav_recipe = get_object_or_404(
            Recipe,
            pk=kwargs['recipe_id']
        )
        instance = get_object_or_404(
            Favorite,
            user=request.user,
            recipe=fav_recipe)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
