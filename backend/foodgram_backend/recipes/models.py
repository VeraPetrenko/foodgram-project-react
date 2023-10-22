from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

from core.models import CreatedModel
from core.validators import validate_slug


NAME_LENGTH = 200
SLUG_LENGTH = 200


User = get_user_model()


class Tag(CreatedModel):
    """Модель тегов."""
    name = models.CharField(
        "Название тега",
        max_length=NAME_LENGTH,
        unique=True,
    )
    color = models.CharField(
        max_length=31,
        null=True,
        default="#ffffff",
        unique=True,
    )
    slug = models.SlugField(
        "Уникальный слаг тега",
        max_length=SLUG_LENGTH,
        unique=True,
        validators=(validate_slug,),
    )

    def __str__(self):
        return self.name[0:15]


class Recipe(CreatedModel):
    """Модель рецептов."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор рецепта",
        related_name="recipes",
    )
    name = models.CharField(
        verbose_name="Название рецепта",
        max_length=200,
    )
    image = models.ImageField(
        upload_to="media/",
        null=True,
        default=None,
    )
    text = models.TextField(
        verbose_name="Описание рецепта",
    )
    ingredients = models.ManyToManyField(
        "Ingredient",
        through="IngredientRecipe",
        verbose_name="Ингредиенты рецепта",
    )
    tags = models.ManyToManyField(
        "Tag",
        through="TagRecipe",
        verbose_name="Теги рецепта",
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )

    class Meta:
        ordering = ("-pub_date",)

    def __str__(self):
        return self.name[0:15]


class Ingredient(CreatedModel):
    """Модель ингредиентов."""
    name = models.CharField(
        "Название ингредиента",
        max_length=NAME_LENGTH,
    )
    measurement_unit = models.CharField(
        "Название единицы измерения",
        max_length=NAME_LENGTH,
    )

    def __str__(self):
        return self.name[0:15]


class IngredientRecipe(models.Model):
    """Модель связи ингредиентов и рецептов."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredient_recipe",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredient_recipe",
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
        related_name="tag_recipe",
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="tag_recipe",
    )


class Follow(CreatedModel):
    """Модель подписок на пользователей."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Фолловер",
        related_name="follower",
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор постов",
        related_name="following",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "following"], name="unique_user_following"
            )
        ]

    def __str__(self):
        return f"Подписка {self.user.username}" f"на {self.following.username}"


class Favorite(CreatedModel):
    """Модель избранного."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorite_recipe",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite_recipe",
    )

    class Meta:
        unique_together = ("user", "recipe")

    def __str__(self):
        return (
            f"Избранное пользователя {self.user.username} - "
            f"рецепт {self.recipe.name}"
        )


class ShoppingCart(CreatedModel):
    """Модель для списка покупок."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="cart_recipe",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cart_recipe",
    )

    class Meta:
        unique_together = ("user", "recipe")

    def __str__(self):
        return (
            f"Корзина пользователя {self.user.username} - "
            f"рецепт {self.recipe.name}"
        )
