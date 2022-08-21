from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientSearchFilter, RecipeFilter
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)
from .pagination import CustomPageNumberPagination
from .permissions import isAuthorOrAdmin
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeListSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny, ]
    http_method_names = ['get', ]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny, ]
    http_method_names = ['get', ]
    pagination_class = None
    filter_backends = [IngredientSearchFilter]
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            self.permission_classes = [AllowAny]
        elif self.action == 'create':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [isAuthorOrAdmin]
        return super().get_permissions()

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = FavoriteSerializer(data=data,
                                        context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @favorite.mapping.delete
    def favorite_delete(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = get_object_or_404(Favorite, user=user, recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = ShoppingCartSerializer(data=data,
                                            context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        cart = get_object_or_404(ShoppingCart, user=user, recipe=recipe)
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__carts__user=request.user).values(
                'ingredient__name',
                'ingredient__measurement_unit'
        ).annotate(Sum('amount'))

        if not ingredients:
            return Response({'error': 'Ваша корзина пуста'},
                            status=status.HTTP_400_BAD_REQUEST)

        shop_list = 'Список покупок \n\n'
        for ingredient in ingredients:
            shop_list += (
                f"{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['amount__sum']}\n"
            )
        return HttpResponse(shop_list, content_type='text/plain')
