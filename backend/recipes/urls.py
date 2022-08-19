from django.urls import include, path
from rest_framework import routers

from .views import IngredientViewSet, RecipeViewSet, TagViewSet

app_name = 'recipes'


router_tags = routers.DefaultRouter()
router_tags.register(
    'tags', TagViewSet, basename='tags'
)

router_ingredients = routers.DefaultRouter()
router_ingredients.register(
    'ingredients', IngredientViewSet, basename='ingredients'
)

router_recipe = routers.DefaultRouter()
router_recipe.register(
    'recipes', RecipeViewSet, basename='recipes'
)

patterns = [
    path('', include(router_tags.urls)),
    path('', include(router_ingredients.urls)),
    path('', include(router_recipe.urls)),
]

urlpatterns = [
    path('', include(patterns)),
]
