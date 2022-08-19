from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name=_('Название'),
        max_length=150,
        unique=True,
        null=False,
        help_text='Название тега',
    )
    color = ColorField(
        default='#FF0000',
        verbose_name=_('HEX-код цвета'),
        unique=True,
        null=True,
        help_text='Выберите цвет',
    )
    slug = models.SlugField(
        verbose_name=_('Адрес'),
        unique=True,
        help_text='Придумайте уникальный URL адрес для тега',
    )
    REQUIRED_FIELDS = ['name', 'color', 'slug']

    class Meta:
        ordering = ('name',)
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name=_('Название'),
        max_length=200,
        blank=False,
        help_text='Введите название ингредиента',
    )
    measurement_unit = models.CharField(
        verbose_name=_('Единица измерения'),
        max_length=50,
        blank=False,
        help_text='Введите единицу измерения',
    )
    REQUIRED_FIELDS = ['name', 'measurement_unit']

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='name_unit_uniq'),
        )
        ordering = ('name',)
        verbose_name = _('Ингредиент')
        verbose_name_plural = _('Ингредиенты')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        verbose_name=_('Название'),
        max_length=200,
        unique=True,
        help_text='Укажите название рецепта',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name=_('Автор рецепта'),
        help_text='Автор рецепта',
    )
    text = models.TextField(verbose_name=_('Описание'))
    tags = models.ManyToManyField(
        Tag,
        verbose_name=_('Теги'),
        related_name='recipes',
        help_text='Выберите теги',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name=_('Ингредиенты рецепта'),
        help_text='Выберите ингредиенты',
    )
    image = models.ImageField(
        verbose_name=_('Фото блюда'),
        upload_to='recipe/',
        help_text='Загрузите изображение с фотографией готового блюда',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1),),
        verbose_name=_('Время приготовления'),
        help_text='Задайте время приготовления блюда',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепты')

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='amounts',
        verbose_name=_('Рецепт'),
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='amounts',
        verbose_name=_('Ингредиент'),
    )
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(
            1,
            message='Укажите количество больше нуля!',
        ),),
        verbose_name=_('Количество'),
        help_text='Количество единиц ингредиента',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient',),
                name='recipe_ingredient_exists'),
            models.CheckConstraint(
                check=models.Q(amount__gte=1),
                name='amount_gte_1'),
        )
        verbose_name = _('Ингредиент в рецепте')
        verbose_name_plural = _('Ингредиенты в рецепте')


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name=_('Пользователь'),
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name=_('Рецепт'),
    )

    class Meta:
        verbose_name = _('Избранное')
        verbose_name_plural = _('Избранные')
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique favorite')
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name=_('Пользователь'),
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name=_('Рецепт'),
    )

    class Meta:
        verbose_name = _('Корзина')
        verbose_name_plural = _('Корзина')
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique shopping cart')
        ]
