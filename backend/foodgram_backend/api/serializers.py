import base64
from django.core.files.base import ContentFile
from rest_framework.validators import UniqueTogetherValidator
from rest_framework import serializers
from djoser.serializers import UserSerializer
from django.shortcuts import get_object_or_404

from recipes.models import (
    Ingredient,
    # Favorites,
    Follow,
    Recipe,
    IngredientRecipe,
    Tag,
    TagRecipe,
)
from users.models import User


class UserSerializer(UserSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            # 'is_subscribed',
        )


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
    # можно в name measurement_unit использовать ReadOnlyField
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
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
    

    class Meta:
        model = Recipe
        fields = '__all__'


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


class RecipeCreateSerializer(serializers.ModelSerializer):
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
    # tags = TagRecipeCreateSerializer(
    #     many=True,
    #     source='tag_recipe'
    # )

    # tags = TagSerializer(many=True, )

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


class FollowSerializer(serializers.ModelSerializer):
    # написать сериализатор для отображения списка подписок
    # following = serializers.SlugRelatedField(
    #     queryset=User.objects.all(),
    #     slug_field='username',
    #     read_only=False
    # )
    # user = serializers.SlugRelatedField(
    #     read_only=True,
    #     slug_field='username',
    #     default=serializers.CurrentUserDefault()
    # )
    # recipes = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'user',
            'following',
            # 'recipes',
        )
        model = Follow
        validators = (
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following')
            ),
        )

    def validate_following(self, value):
        if self.context['request'].user == value:
            raise serializers.ValidationError(
                'Невозможно подписаться на себя'
            )
        return value
    
    # def get_recipes(self, instance):
    #     recipes = instance.following.recipe.objects.all()
    #     return RecipeInFollowSerializer(recipes, many=True, context=self.context).data


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


# class RecipeInFollowSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Recipe
#         fields = (
#             'id',
#             'name',
#             'image',
#             'cooking_time',
#         )
