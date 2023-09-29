from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

from core.models import CreatedModel


User = get_user_model()
NAME_LENGTH = 200
SLUG_LENGTH = 200


class Tag(CreatedModel):
    """Модель тегов."""
    name = models.CharField(
        'Название тега',
        max_length=NAME_LENGTH,
        unique=True,
    )
    color = models.CharField(
        max_length=7,
        null=True,
        default='#ffffff',
        unique=True,
    )
    # сделать валидатор в сериалайзере ^[-a-zA-Z0-9_]+$
    slug = models.SlugField(
        'Уникальный слаг тега',
        max_length=SLUG_LENGTH,
        unique=True,
    )


class Recipe(CreatedModel):
    """Модель рецептов."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipes'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200
    )
    image = models.ImageField(
        upload_to='recipes/images',
        null=True,
        default=None
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='IngredientRecipe',
        verbose_name='Ингредиенты рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги рецепта'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )


class Ingredient(CreatedModel):
    """Модель ингредиентов."""
    name = models.CharField(
        'Название ингредиента',
        max_length=NAME_LENGTH,
    )
    measurement_unit = models.CharField(
        'Название единицы измерения',
        max_length=NAME_LENGTH,
    )


class IngredientRecipe(models.Model):
    """Модель связи ингредиентов и рецептов."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe'
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        default=1
    )


# class Follow(CreatedModel):
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='follower'
#     )
#     author = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='following'
#     )

#     class Meta:
#         unique_together = ('user', 'author')


# class Favorites(CreatedModel):
#     """Модель избранного."""
#     recipe = models.ForeignKey(
#         Recipe,
#         on_delete=models.CASCADE,
#         related_name='favorite_recipe',
#     )
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='follower_recipe',
#     )

#     class Meta:
#         unique_together = ('user', 'recipe')