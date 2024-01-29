from rest_framework import permissions
from AgentManager import models
from AgentManager import serializers

class outContextpermissions(permissions.BasePermission):
    """allow users to edit their own profiles"""
    message = 'Access denied'
    def has_object_permission(seuser_profilelf, request, view, obj):
        """Check user is trying to edit their own profile"""

        if request.method in permissions.SAFE_METHODS:
             return True
        else:
            return False

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
             return True
        else:
            return False
class AgentStatusPemissions(permissions.BasePermission):
    message='Access denied'
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        else:
            return False

class AgentInfoPemissions(permissions.BasePermission):
    message='Access denied'
    def has_permission(self, request, view):
        if request.user.is_superuser and request.method in permissions.SAFE_METHODS:
            return True
        else:
            return False

class AgentPermissions(permissions.BasePermission):
    """allow users to edit their own profiles"""
    message = 'Access denied'

    def has_permission(self, request, view):
        if ("/agent/" in request.path) or ("/defaultagent/" in request.path and (request.user.is_superuser)):
             return True
        else:
            return False

    def has_object_permission(seuser_profilelf, request, view, obj):
        """Check user is trying to edit their own profile"""
        if "/defaultagent/" in request.path and (request.user.is_superuser):
            return True
        elif "/defaultagent/" in request.path and not (request.user.is_superuser):
            return False
        if "/agent/" in request.path:
            if (request.method in permissions.SAFE_METHODS) or (request.user.is_superuser):
                 return True

            permissions_list = models.UserPermissions.objects.filter(agent=obj, user_profile=request.user)
            if len(permissions_list) != 0:
                if ((permissions_list[0].is_admin == True) and (permissions_list[0].is_active == True)):
                    return True
            else:
                return False



class DefaultIntentsPermissions(permissions.BasePermission):
    """allow users to edit their own profiles"""
    message = 'Access denied'
    def has_object_permission(seuser_profilelf, request, view, obj):
        """Check user is trying to edit their own profile"""

        if (request.method in permissions.SAFE_METHODS):
             return True
        else:
            return False

    def has_permission(self, request, view):
        if (request.method in permissions.SAFE_METHODS):
            return True
        else:
            return False

class Stop_Agent_Permission(permissions.BasePermission):
    message = "Access denied"
    def has_permission(self, request, view):
        agent_id = request.data['agent_id']
        try:
            agent = models.Agent.objects.get(id =agent_id)
        except:
            return False
        try:
            permission = models.UserPermissions.objects.get(agent = agent, user_profile = request.user)
        except:
            return False
        if permission.is_admin:
            return True
        else:
            return False

class AddDefaultIntentManagerPermission(permissions.BasePermission):
    """allow users to edit their own profiles"""
    message = 'Access denied'
    def has_object_permission(seuser_profilelf, request, view, obj):
        """Check user is trying to edit their own profile"""
        return False

    def has_permission(self, request, view):
        agentID=request.resolver_match.kwargs.get('agentid')
        try:
            consideredAgent = models.Agent.objects.get(id=agentID)
        except(TypeError, ValueError, OverflowError, models.Agent.DoesNotExist):
            return False

        try:
            permissions = models.UserPermissions.objects.get(agent=consideredAgent, user_profile=request.user)
        except(TypeError, ValueError, OverflowError, models.UserPermissions.DoesNotExist):
            return False
        if permissions.creating_access and permissions.is_active == True:
            return True
        else:
            return False


class IntentPermissions(permissions.BasePermission):
    """allow users to edit the intent according to the given permissions"""
    message = 'Access denied'
    def has_object_permission(seuser_profilelf, request, view, obj):
        """Check user is trying to edit their own profile"""

        try:
            permissions_list = models.UserPermissions.objects.get(agent=obj.agent, user_profile=request.user)
        except(TypeError, ValueError, OverflowError, models.UserPermissions.DoesNotExist):
            return False
        if ((permissions_list.is_admin) and (permissions_list.is_active == True)):
            Authorized_Methods = ('PATCH', 'GET', 'HEAD', 'OPTIONS', 'UPDATE', 'DELETE', 'PUT')
        else:
            Authorized_Methods = ()

        if not permissions_list.is_admin and permissions_list.reading_access and permissions_list.is_active == True:
            Authorized_Methods=permissions.SAFE_METHODS

        if not permissions_list.is_admin and permissions_list.creating_access and permissions_list.is_active == True:
            Authorized_Methods=Authorized_Methods+('POST',)

        if not permissions_list.is_admin and permissions_list.updating_access and permissions_list.is_active == True:
            Authorized_Methods=Authorized_Methods+('UPDATE',)
            Authorized_Methods=Authorized_Methods+('PUT',)
            Authorized_Methods=Authorized_Methods+('PATCH',)

        if not permissions_list.is_admin and permissions_list.deleting_access and permissions_list.is_active == True:
            Authorized_Methods=Authorized_Methods+('DELETE',)

        if request.method in Authorized_Methods:
             return True
        else:
            return False

    def has_permission(self, request, view):
        """Check user is trying to edit the users permission of its own agent"""
        agentid = request.resolver_match.kwargs.get('agentid')


        try:
            consideredAgent = models.Agent.objects.get(id=agentid)
        except(TypeError, ValueError, OverflowError, models.Agent.DoesNotExist):
            return False

        try:
            permissions_list = models.UserPermissions.objects.get(agent=consideredAgent, user_profile=request.user)
        except(TypeError, ValueError, OverflowError, models.UserPermissions.DoesNotExist):
            return False
        if permissions_list.is_admin and permissions_list.is_active == True:
            Authorized_Methods = ('PATCH', 'GET', 'HEAD', 'OPTIONS', 'UPDATE', 'DELETE', 'PUT', 'POST')
        else:
            Authorized_Methods = ()

        if not permissions_list.is_admin and permissions_list.reading_access and permissions_list.is_active == True:
            Authorized_Methods = permissions.SAFE_METHODS

        if not permissions_list.is_admin and permissions_list.creating_access and permissions_list.is_active == True:
            Authorized_Methods = Authorized_Methods + ('GET','POST',)

        if not permissions_list.is_admin and permissions_list.updating_access and permissions_list.is_active == True:
            Authorized_Methods = Authorized_Methods + ('UPDATE',)
            Authorized_Methods = Authorized_Methods + ('PUT',)
            Authorized_Methods = Authorized_Methods + ('PATCH',)

        if not permissions_list.is_admin and permissions_list.deleting_access and permissions_list.is_active == True:
            Authorized_Methods = Authorized_Methods + ('DELETE',)

        if request.method in Authorized_Methods:
            return True
        else:
            return False

class ExportIntentPermissions(permissions.BasePermission):
    """     Handle the permissions of export agents"""

    def has_permission(self, request, view):
        """Check user is trying to edit the users permission of its own agent"""
        agentid = request.resolver_match.kwargs.get('agentid')

        try:
            consideredAgent = models.Agent.objects.get(id=agentid)
        except(TypeError, ValueError, OverflowError, models.Agent.DoesNotExist):
            return False

        try:
            permissions_list = models.UserPermissions.objects.get(agent=consideredAgent, user_profile=request.user)
        except(TypeError, ValueError, OverflowError, models.UserPermissions.DoesNotExist):
            return False
        if permissions_list.is_admin and permissions_list.is_active == True:
            Authorized_Methods = ('PATCH', 'GET', 'HEAD', 'OPTIONS', 'UPDATE', 'DELETE', 'PUT', 'POST')
        else:
            Authorized_Methods = ()

        if not permissions_list.is_admin and permissions_list.reading_access and permissions_list.is_active == True:
            Authorized_Methods = permissions.SAFE_METHODS+('POST',)

        if not permissions_list.is_admin and permissions_list.creating_access and permissions_list.is_active == True:
            #Authorized_Methods = Authorized_Methods + ('POST',)
            pass

        if not permissions_list.is_admin and permissions_list.updating_access and permissions_list.is_active == True:
            Authorized_Methods = Authorized_Methods + ('UPDATE',)
            Authorized_Methods = Authorized_Methods + ('PUT',)
            Authorized_Methods = Authorized_Methods + ('PATCH',)

        if not permissions_list.is_admin and permissions_list.deleting_access and permissions_list.is_active == True:
            Authorized_Methods = Authorized_Methods + ('DELETE',)

        if request.method in Authorized_Methods:
            return True
        else:
            return False

class UserManagePermissions(permissions.BasePermission):
    """Manage users permission of the considered agent"""

    message = 'Access denied'


    def has_object_permission(seuser_profilelf, request, view, obj):
        """Check user is trying to edit the users permission of its own agent"""

        try:
            permissions_list = models.UserPermissions.objects.get(agent=obj.agent, user_profile=request.user)
        except(TypeError, ValueError, OverflowError, models.UserPermissions.DoesNotExist):
            return False
        if permissions_list.is_admin:
            Authorized_Methods = ('PATCH', 'GET', 'HEAD', 'OPTIONS', 'UPDATE', 'DELETE', 'PUT')
        else:
            Authorized_Methods = ('GET', 'HEAD', 'OPTIONS',)

        if obj.user_profile==request.user:
            Authorized_Methods = Authorized_Methods+('DELETE','PATCH')
            serializers.AgentCustomerManagerSerializer.Meta.extra_kwargs = {
                'agent': {'read_only': True},
                'is_admin': {'read_only': True},
                'is_active': {'read_only': False},
                'user_profile': {'read_only': True},
                'creating_access': {'read_only': True},
                'reading_access': {'read_only': True},
                'updating_access': {'read_only': True},
                'deleting_access': {'read_only': True},


            }


        if request.method in Authorized_Methods:
             return True
        else:
            return False


    def has_permission(self, request, view):
        """Check user is trying to edit the users permission of its own agent"""
        agentid = request.resolver_match.kwargs.get('agentid')

        try:
            consideredAgent = models.Agent.objects.get(id=agentid)
        except(TypeError, ValueError, OverflowError, models.Agent.DoesNotExist):
            return False

        try:
            permissions_list = models.UserPermissions.objects.get(agent=consideredAgent, user_profile=request.user)
        except(TypeError, ValueError, OverflowError, models.UserPermissions.DoesNotExist):
            return False
        if permissions_list.is_admin:
            Authorized_Methods = ('PATCH', 'GET', 'HEAD', 'OPTIONS', 'UPDATE', 'DELETE', 'PUT','POST')
        else:
            Authorized_Methods = ('GET', 'HEAD', 'OPTIONS','DELETE', 'PATCH')

        if request.method in Authorized_Methods:
             return True
        else:
            return False



class TrainngManagePermissions(permissions.BasePermission):
    """Manage users permission of the considered agent"""

    message = 'Access denied'


    def has_object_permission(seuser_profilelf, request, view, obj):
        """Check user is trying to edit the users permission of its own agent"""
        return False


    def has_permission(self, request, view):
        """Check user is trying to edit the users permission of its own agent"""
        agentid = request.data['agent_id']

        try:
            consideredAgent = models.Agent.objects.get(id=agentid)
        except(TypeError, ValueError, OverflowError, models.Agent.DoesNotExist):
            return False
        if request.user.is_superuser:
            return True

        try:
            permissions_list = models.UserPermissions.objects.get(agent=consideredAgent, user_profile=request.user)
        except(TypeError, ValueError, OverflowError, models.UserPermissions.DoesNotExist):
            return False
        if permissions_list.is_admin:

             return True
        else:
            return False


class AgentMenuWidgetPermission(permissions.BasePermission):
    message='Access denied'
    def has_permission(self, request, view):
        if request.user.is_superuser and request.method in permissions.SAFE_METHODS:
            return True
        else:
            return False