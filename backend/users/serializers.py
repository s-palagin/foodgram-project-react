from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from .models import User, Follow
from recipes.models import Recipe


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'password')
        model = User
        extra_kwargs = {
            'password': {'write_only': True, 'required': True, },
            'last_name': {'required': True, },
            'first_name': {'required': True, },
            'username': {'required': True, },
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(
            validated_data.get('password')
        )
        return super(UserSerializer, self).create(validated_data)

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                ['Using "me" as username is forbidden.']
            )
        return value

    def validate_password(self, value):
        password_validation.validate_password(value, self.instance)
        return value


class UserMeSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class ChangePasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(write_only=True, required=True)
    current_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('current_password', 'password', 'new_password')

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                "Current password is not correct"
            )
        return value

    def validate_new_password(self, value):
        password_validation.validate_password(value, self.instance)
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance


class BriefRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerilaizer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Follow
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

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user:
            return False
        return Follow.objects.filter(user=user, author=obj.author_id).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = Recipe.objects.filter(
                author=obj.author_id).all()[:(int(recipes_limit))]
        else:
            recipes = Recipe.objects.filter(author=obj.author_id).all()
        context = {'request': request}
        return BriefRecipeSerializer(recipes, many=True,
                                     context=context).data

    @staticmethod
    def get_recipes_count(obj):
        return Recipe.objects.filter(author=obj.author_id).count()