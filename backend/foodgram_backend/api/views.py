from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from djoser.serializers import SetPasswordSerializer
from rest_framework import permissions
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import (
    TagSerializer,
    RecipeSerializer,
    RecipeCreateUpdateSerializer,
    IngredientSerializer,
    FollowSerializer,
    FollowCreateDeleteSerializer,
    UserSerializer,
    UserCreateSerializer,
    FavoriteCreateDeleteSerializer,
    CartAddDeleteSerializer,
)
from core import filters_custom
from recipes.models import (
    Recipe,
    Tag,
    Ingredient,
    Follow,
    Favorite,
    ShoppingCart,
    IngredientRecipe,
)
from users.permissions import (
    IsAdminOrReadOnly,
    IsAdminOrOwner,
)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        request.data["username"] = request.user.username
        serializer = SetPasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["get"], detail=False)
    def me(self, request):
        user = get_object_or_404(User, id=request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action == "set_password":
            return SetPasswordSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == "me" or self.action == "set_password":
            self.permission_classes = (permissions.IsAuthenticated,)
        return super().get_permissions()


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = filters_custom.FilterIngredient


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = filters_custom.FilterRecipe
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            "ingredient_recipe__ingredient", "tags"
        ).all()
        return recipes

    def get_serializer_class(self):
        if self.action == "create" or self.action == "update":
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = RecipeCreateUpdateSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    @action(["get"], detail=False)
    def download_shopping_cart(self, request, *args, **kwargs):
        ingredients_with_amount = list(
            IngredientRecipe.objects.filter(
                recipe__cart_recipe__user=self.request.user
            ).values("ingredient__name", "ingredient__measurement_unit", "amount")
        )
        ingredients = {}
        for ingredient in ingredients_with_amount:
            ingr = ingredient["ingredient__name"]
            if ingr not in ingredients.keys():
                ingredients[ingr] = [
                    ingredient["ingredient__measurement_unit"],
                    ingredient["amount"],
                ]
            else:
                ingredients[ingr][1] += ingredient["amount"]

        shopping_list_file: str = "Список ингредиентов к покупке:" + "\n"
        for ingredient in ingredients:
            shopping_list_file += (
                f"• {ingredient} "
                f"({ingredients[ingredient][0]}) - "
                f"{ingredients[ingredient][1]}"
            ) + "\n"
        return HttpResponse(shopping_list_file, content_type="text/plain")

    def get_permissions(self):
        if self.action == "get":
            self.permission_classes = (permissions.AllowAny,)
        elif self.action == "update" or (self.action == "download_shopping_cart"):
            self.permission_classes = (IsAdminOrOwner,)
        return super().get_permissions()


class FollowViewSet(ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAdminOrOwner,
    )

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        following = get_object_or_404(User, pk=kwargs["following_id"])
        instance = get_object_or_404(Follow, user=request.user, following=following)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if self.action == "create" or self.action == "destroy":
            return FollowCreateDeleteSerializer
        return FollowSerializer


class FollowListViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAdminOrOwner,
    )

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)


class FavoriteViewSet(ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteCreateDeleteSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAdminOrOwner,
    )

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        fav_recipe = get_object_or_404(Recipe, pk=kwargs["recipe_id"])
        instance = get_object_or_404(Favorite, user=request.user, recipe=fav_recipe)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartViewSet(ModelViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = CartAddDeleteSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAdminOrOwner,
    )

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        cart_recipe = get_object_or_404(Recipe, pk=kwargs["recipe_id"])
        instance = get_object_or_404(
            ShoppingCart, user=request.user, recipe=cart_recipe
        )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
