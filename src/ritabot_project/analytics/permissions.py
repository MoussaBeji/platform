
from rest_framework import permissions

class AnalyticsPermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_superuser and (request.method=='POST' or request.method in permissions.SAFE_METHODS):
            return True
        elif not request.user.is_superuser and request.method in permissions.SAFE_METHODS:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return False

class UserinfoPermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        elif not request.user.is_superuser and request.method in permissions.SAFE_METHODS:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        else:
            return False