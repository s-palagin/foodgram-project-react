from django.utils.translation import gettext_lazy as _
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Follow, User
from .serializers import (
    ChangePasswordSerializer, SubscriptionsSerilaizer,
    UserMeSerializer, UserSerializer
)
from recipes.pagination import CustomPageNumberPagination


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    lookup_field = 'id'
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    pagination_class = CustomPageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(detail=False, methods=('get', ),
            permission_classes=(IsAuthenticated,),
            serializer_class=UserMeSerializer)
    def me(self, request):
        serializer = self.get_serializer(instance=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'],
            permission_classes=[IsAuthenticated],
            serializer_class=ChangePasswordSerializer)
    def set_password(self, request, pk=None):
        serializer = self.get_serializer(
            instance=request.user, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = Follow.objects.filter(user=user)
        paginator = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerilaizer(
            paginator,
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', ],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        if user == author:
            return Response(
                {'errors': _('Нельзя подписаться на самого себя')},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Follow.objects.filter(user=user, author=author).exists():
            return Response(
                {'errors': _('Подписка уже существует')},
                status=status.HTTP_400_BAD_REQUEST
            )

        follow = Follow.objects.create(user=user, author=author)
        serializer = SubscriptionsSerilaizer(
            follow, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        follow = Follow.objects.filter(user=user, author=author)
        if follow.exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'errors': _('Нет подписки на этого автора')},
            status=status.HTTP_400_BAD_REQUEST
        )
