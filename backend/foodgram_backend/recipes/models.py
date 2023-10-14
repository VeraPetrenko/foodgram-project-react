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
        upload_to='',
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
        'Tag',
        through='TagRecipe',
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


class TagRecipe(models.Model):
    """Модель связи тегов и рецептов."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='tag_recipe'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tag_recipe'
    )


class Follow(CreatedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Фолловер',
        related_name='follower'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор постов',
        related_name='following'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'
            )
        ]

    def __str__(self):
        return f'Подписка на {self.following.username}'


class Favorite(CreatedModel):
    """Модель избранного."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
    )

    class Meta:
        unique_together = ('user', 'recipe')
