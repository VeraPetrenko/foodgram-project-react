import base64
from django.core.files.base import ContentFile
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
import djoser.serializers
from django.shortcuts import get_object_or_404

from recipes.models import (
    Ingredient,
    Favorite,
    Follow,
    Recipe,
    IngredientRecipe,
    Tag,
    TagRecipe,
    ShoppingCart
)
from users.models import User
from core.validators import validate_username


class UserSerializer(djoser.serializers.UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, instance):
        request = self.context.get('request')
        if not request:
            return False
        return Follow.objects.filter(
            user=request.user,
            following=instance
            ).exists()


class UserCreateSerializer(djoser.serializers.UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def validate_username(self, value):
        if value and User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username уже занят.')
        validate_username(value)
        return value


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class TagRecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='tag',
        queryset=Tag.objects.all(),
    )
    name = serializers.ReadOnlyField(source='tag.name')
    color = serializers.ReadOnlyField(source='tag.color')
    slug = serializers.ReadOnlyField(source='tag.slug')

    class Meta:
        model = TagRecipe
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class TagRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='tag.id')
    name = serializers.CharField(source='tag.name')
    color = serializers.CharField(
        source='tag.color'
    )
    slug = serializers.CharField(
        source='tag.slug'
    )

    class Meta:
        model = TagRecipe
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagRecipeSerializer(many=True, source='tag_recipe')
    ingredients = IngredientRecipeSerializer(many=True, source='ingredient_recipe')
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, instance):
        return Favorite.objects.filter(
            user=self.context['request'].user,
            recipe=instance
        ).exists()

    def get_is_in_shopping_cart(self, instance):
        return ShoppingCart.objects.filter(
            user=self.context['request'].user,
            recipe=instance
        ).exists()


class IngredientRecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all(),
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeCreateSerializer(
        many=True,
        source='ingredient_recipe'
    )
    image = Base64ImageField(
        required=False,
        allow_null=True
    )
    author = UserSerializer(read_only=True)

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredient_recipe')
        tags = validated_data.pop('tags')
        instance = super().create(validated_data)
        # здесь нужно поменять на балк креэйт:
        for tag in tags:
            TagRecipe(
                tag=Tag.objects.get(id=tag.id),
                recipe=instance
            ).save()
        for ingredient_data in ingredients:
            IngredientRecipe(
                recipe=instance,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            ).save()
        return instance

    def to_representation(self, instance):
        representation = super(RecipeCreateUpdateSerializer, self).to_representation(instance)
        representation['tags'] = TagSerializer(instance.tags.all(), many=True).data
        return representation

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredient_recipe')
        instance.ingredients.clear()
        new_tags = []
        for tag in tags:
            new_tags.append(tag.id)
        instance.tags.set(new_tags)
        for ingredient_data in ingredients:
            IngredientRecipe.objects.update_or_create(
                recipe=instance,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            )
        return super().update(instance, validated_data)

    def validate(self, attrs):
        if len(attrs['tags']) < 1:
            return ValidationError('Не выбрано ни одного тега.')
        if len(set(attrs['tags'])) != len(attrs['tags']):
            return ValidationError('Теги дублируются.')
        if len(attrs['ingredient_recipe']) < 1:
            return ValidationError('Не указан ни один ингредиент.')
        ingredients = [ingredient['ingredient'].id for ingredient in attrs['ingredient_recipe']]
        if len(set(ingredients)) != (
            len(attrs['ingredient_recipe'])
        ):
            return ValidationError('Ингредиенты дублируются.')
        return super().validate(attrs)


class FollowCreateDeleteSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='follow.user')
    following = serializers.ReadOnlyField(source='follow.following')

    class Meta:
        model = Follow
        fields = ('user', 'following',)

    def create(self, validated_data):
        user = validated_data['user']
        following = get_object_or_404(
            User,
            pk=self.context['view'].kwargs['following_id']
        )
        subscribtion = Follow(user=user, following=following)
        subscribtion.save()
        return subscribtion

    def validate_following(self, value):
        user = self.context['request'].user
        if user == value:
            raise serializers.ValidationError(
                'Невозможно подписаться на себя'
            )
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        following = get_object_or_404(
            User,
            pk=self.context['request'].parser_context['kwargs']['following_id']
        )
        if len(Follow.objects.filter(user=user, following=following)) > 0:
            raise serializers.ValidationError(
                'Подписка уже существует'
            )
        return super().validate(attrs)


class RecipeInFollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения подписок."""
    email = serializers.ReadOnlyField(source='following.email')
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, instance):
        if Follow.objects.filter(
            user=instance.user,
            following=instance.following
        ).exists():
            return True
        return False

    def get_recipes_count(self, instance):
        return Recipe.objects.filter(author=instance.following).count()

    def get_recipes(self, instance):
        recipes = Recipe.objects.filter(author=instance.following)
        return RecipeInFollowSerializer(
            recipes,
            many=True,
            context=self.context
        ).data


class FavoriteCreateDeleteSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='favorite.user')
    recipe = serializers.ReadOnlyField(source='favorite.recipe')

    class Meta:
        model = Favorite
        fields = ('user', 'recipe',)

    def create(self, validated_data):
        user = validated_data['user']
        recipe = get_object_or_404(
            Recipe,
            pk=self.context['view'].kwargs['recipe_id']
        )
        fav_rec = Favorite(user=user, recipe=recipe)
        fav_rec.save()
        return fav_rec

    def validate(self, attrs):
        user = self.context['request'].user
        recipe = get_object_or_404(
            Recipe,
            pk=self.context['request'].parser_context['kwargs']['recipe_id']
        )
        if len(Favorite.objects.filter(user=user, recipe=recipe)) > 0:
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное'
            )
        return super().validate(attrs)


class CartAddDeleteSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='shoppingcart.user')
    recipe = serializers.SerializerMethodField()

    class Meta:
        model = Favorite
        fields = ('user', 'recipe',)

    def create(self, validated_data):
        user = validated_data['user']
        recipe = get_object_or_404(
            Recipe,
            pk=self.context['view'].kwargs['recipe_id']
        )
        cart_rec = ShoppingCart(user=user, recipe=recipe)
        cart_rec.save()
        return cart_rec

    def get_recipe(self, instance):
        recipe = instance.recipe
        return RecipeInFollowSerializer(
            recipe,
            context=self.context
        ).data

    def validate(self, attrs):
        user = self.context['request'].user
        recipe = get_object_or_404(
            Recipe,
            pk=self.context['request'].parser_context['kwargs']['recipe_id']
        )
        if len(ShoppingCart.objects.filter(user=user, recipe=recipe)) > 0:
            raise serializers.ValidationError(
                'Рецепт уже добавлен в корзину'
            )
        return super().validate(attrs)
