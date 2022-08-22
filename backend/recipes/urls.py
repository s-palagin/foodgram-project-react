from django.urls import include, path
from rest_framework import routers

from .views import IngredientViewSet, RecipeViewSet, TagViewSet

app_name = 'recipes'

router_recipe = routers.DefaultRouter()
router_recipe.register(
    'recipes', RecipeViewSet, basename='recipes'
)
router_recipe.register(
    'ingredients', IngredientViewSet, basename='ingredients'
)
router_recipe.register(
    'tags', TagViewSet, basename='tags'
)

patterns = [
    path('', include(router_recipe.urls)),
]

urlpatterns = [
    path('', include(patterns)),
]
