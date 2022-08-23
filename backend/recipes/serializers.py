from django.utils.translation import gettext_lazy as _
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import (
    Favorite, Ingredient, Recipe, RecipeIngredient,
    ShoppingCart, Tag
)
from users.serializers import BriefRecipeSerializer, UserSerializer


class TagSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all())

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):

    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    author = UserSerializer(read_only=True)
    ingredients = AddIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'text',
            'tags',
            'ingredients',
            'image',
            'cooking_time'
        )

    def validate(self, data):
        required_filds = [
            'name', 'text', 'cooking_time',
            'image', 'tags', 'ingredients',
        ]
        for field in required_filds:
            if not data.get(field):
                raise serializers.ValidationError(
                    f'{field}: _(Обязательное поле)'
                )

        ingredients = data.get('ingredients')
        ingredients_list = []
        for ingredient in ingredients:
            required_ingredient_filds = [
                'id', 'amount',
            ]
            for field in required_ingredient_filds:
                if not ingredient.get(field):
                    raise serializers.ValidationError(
                        f'{field}: _(Обязательное поле в ingredients)'
                    )
            ingredient_id = ingredient.get('id')
            amount = ingredient.get('amount')
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError({
                    'ingredients': _('Ингредиенты должны быть уникальными!')
                })
            ingredients_list.append(ingredient_id)
            if int(amount) <= 0:
                raise serializers.ValidationError({
                    'amount': _('Неверное количество ингредиента')
                })

        tags = data.get('tags')
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError({
                    'tags': _('Тэги должны быть уникальными!')
                })
            tags_list.append(tag)

        return data

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_tags(validated_data.pop('tags'), instance)
        self.create_ingredients(validated_data.pop('ingredients'), instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance, context={'request': self.context.get('request')}).data

    @staticmethod
    def create_ingredients(ingredients, recipe):
        new_ingredients = []
        for ingredient in ingredients:
            adding_ingredient = RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
            new_ingredients.append(adding_ingredient)
        RecipeIngredient.objects.bulk_create(new_ingredients)

    @staticmethod
    def create_tags(tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'text',
            'tags',
            'ingredients',
            'image',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )


    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(favorites__user=user, id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(carts__user=user, id=obj.id).exists()


class ModelSerializerWithRepresentashion(serializers.ModelSerializer):

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return BriefRecipeSerializer(
            instance.recipe, context=context).data


class FavoriteSerializer(ModelSerializerWithRepresentashion):

    class Meta:
        model = Favorite
        fields = ('id', 'user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        recipe = data['recipe']
        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'errors': _('Рецепт уже в избранном!')}
            )
        return data


class ShoppingCartSerializer(ModelSerializerWithRepresentashion):

    class Meta:
        model = ShoppingCart
        fields = ('id', 'user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        recipe = data['recipe']
        if ShoppingCart.objects.filter(user=request.user,
                                       recipe=recipe).exists():
            raise serializers.ValidationError(
                {'errors': _('Рецепт уже в корзине!')}
            )
        return data
