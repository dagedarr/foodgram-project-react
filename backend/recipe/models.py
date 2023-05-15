from django.core.validators import MinValueValidator
from django.db import models
from users.models import User

COLOR = (
    ('#FF0000', 'Красный'),
    ('#E26C2D', 'Оранжевый'),
    ('#FFFF00', 'Желтый'),
    ('#49B64E', 'Зеленый'),
    ('#0000FF', 'Синий'),
    ('#2E2B5F', 'Индиго'),
    ('#8775D2', 'Фиолетовый'),
)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор публикации',
        related_name='recipies',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        db_index=True,
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='media/',
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='Component',
        verbose_name='Ингредиенты',
        related_name='recipies',
    )
    tags = models.ManyToManyField(
        'Tag',
        verbose_name='Тег',
        related_name='recipies',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления(мин.)',
        validators=[MinValueValidator(1)],
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Тэги для рецептов с предустановленным выбором."""
    name = models.CharField(
        verbose_name='Название тега',
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цветовой HEX-код',
        max_length=7,
        choices=COLOR,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200,
        blank=False,
        db_index=True,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        blank=False,
        max_length=200,
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Component(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='components',
    )
    ingredient = models.ForeignKey(
        'Ingredient',
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='components',
    )

    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'Компонент рецепта'
        verbose_name_plural = 'Компоненты рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_component')
        ]

    def __str__(self):
        return f'{self.ingredient} {self.amount} шт'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        related_name='shopping_cart',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping_cart',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_user_recipe_in_cart')]

    def __str__(self):
        return f'{self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='favorite',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Избранные рецепты',
        related_name='favorite',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Избранные рецепты'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_favorite')]

    def __str__(self):
        return f'{self.recipe}'
