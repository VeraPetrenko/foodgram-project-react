from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag

from recipes.models import (
    Ingredient,
    # Favorites,
    # Follow,
    Recipe,
    IngredientRecipe,
    Tag
)
from users.models import User


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


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
    tags = TagSerializer(many=True)
    ingredients = IngredientRecipeSerializer(many=True, source='ingredient_recipe')

    class Meta:
        model = Recipe
        fields = '__all__'


class IngredientRecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    # дописать
    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measurment_unit',
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
    ingredients = IngredientRecipeCreateSerializer(many=True)
    image = serializers.SerializerMethodField(
        'get_image',
        read_only=True,
    )

    class Meta:
        model = Recipe
        fields = (
            # 'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
        )

    def get_image(self, obj):
        img = Base64ImageField(required=False, allow_null=True)
        if obj.img:
            return obj.img.url
        return None

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance = super().create(validated_data)
        # здесь нужно поменять на балк креэйт:
        for ingredient_data in ingredients:
            IngredientRecipe(
                recipe=instance,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            ).save()
        return instance