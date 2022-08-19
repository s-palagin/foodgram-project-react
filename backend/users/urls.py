from django.urls import include, path
from rest_framework import routers

from .views import UserViewSet

app_name = 'users'


router_users = routers.DefaultRouter()
router_users.register(
    'users', UserViewSet, basename='users'
)

patterns = [
    path('', include(router_users.urls)),
]

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(patterns))
]
