# Create your views here.
from rest_framework import viewsets
from ritabot.settings import *
from external_api.serializers import *
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import filters
from external_api import permissions

"""     Permissions and token import modules    """
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class StudentEnrollmentView(viewsets.ModelViewSet):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, permissions.StudentEnrollmentPermissions)
    serializer_class = StudentEnrollmentSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    queryset = Student.objects.all()

    def create(self, request, *args, **kwargs):
        print("dataaaa :", request.data)
        serializer = StudentEnrollmentSerializer(data=request.data, context={'request': self.request, 'agentid': self.kwargs['agentid']})

        if serializer:
            serializer.create(self.request.data)
            return Response({"success": True})
        raise ValidationError(serializer.error_messages)

    def get_queryset(self):
        agentid = self.kwargs['agentid']
        students = Student.objects.filter(agent=agentid)
        return students
