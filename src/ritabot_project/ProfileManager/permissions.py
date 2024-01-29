from rest_framework import permissions
class UpdateOwnProfile(permissions.BasePermission):
    """allow users to edit their own profiles"""
    message = 'Access denied'
    def has_object_permission(seuser_profilelf, request, view, obj):
        """Check user is trying to edit their own profile"""

        if request.method in permissions.SAFE_METHODS:
             return True
        return obj.id == request.user.id


    def has_permission(self, request, view):

        Authorized_Methods = ('PATCH', 'GET', 'UPDATE','DELETE','PUT')
        if request.method in Authorized_Methods:
            return True
        return False

class UpdateOwnPassword(permissions.BasePermission):
    """allow users to edit their own profiles"""
    message = 'Access denied'
    def has_permission(self, request, view):

        Authorized_Methods = ('POST', 'GET')
        if request.method in Authorized_Methods:
            return True
        return False
