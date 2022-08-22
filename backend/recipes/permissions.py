from rest_framework import permissions


class IsAuthorOrAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated and (
                obj.author == request.user
                or request.user.is_admin
            )
        )
