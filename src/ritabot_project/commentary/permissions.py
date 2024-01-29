from AgentManager import models
from rest_framework import permissions
class default_permission(permissions.BasePermission):
    message = "Access denied"
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        agent_id =request.resolver_match.kwargs.get('agentid')
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