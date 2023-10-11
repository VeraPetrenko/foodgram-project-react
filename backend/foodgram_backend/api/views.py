from django.shortcuts import HttpResponse
from djoser.views import UserViewSet
from django_filters import rest_framework as filters
from rest_framework.viewsets import ModelViewSet
from recipes.models import Recipe, Tag, Ingredient, Follow
from api.serializers import TagSerializer, RecipeSerializer, RecipeCreateSerializer, IngredientSerializer, FollowSerializer, FollowCreateDeleteSerializer, UserSerializer
from core import filters_custom
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


User = get_user_model()


class CustomUserViewSet(UserViewSet):

    # @action(["post", "delete"], detail=False)
    # def subscribe(self, request):
    #     ...

    @action(["get"], detail=False)
    def me(self, request):
        user = get_object_or_404(User, id=request.user.id)
        serializer = UserSerializer(user)
        # пермишн будет только авторизованный
        return Response(serializer.data)

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

    # def get_queryset(self):
    #     return self.request.user.follower.all()
    
    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )
    
    # протестить

    def perform_destroy(self, instance):
        subscription = instance
        subscription.delete()

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'destroy':
            return FollowCreateDeleteSerializer
        return FollowSerializer
