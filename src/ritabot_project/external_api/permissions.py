from rest_framework import permissions
from AgentManager import models


class StudentEnrollmentPermissions(permissions.BasePermission):

    message = 'Access denied'


    def has_permission(self, request, view):
        agentid = request.resolver_match.kwargs.get('agentid')

        try:
            agent = models.Agent.objects.get(id=agentid)
            print("---------- :", agent)
        except(TypeError, ValueError, OverflowError, models.Agent.DoesNotExist):
            return False

        try:
            permissions_list = models.UserPermissions.objects.get(agent=agent, user_profile=request.user, is_active=True)
            print("++++++++++ :", permissions_list)
            return True
        except(TypeError, ValueError, OverflowError, models.UserPermissions.DoesNotExist):
            return False