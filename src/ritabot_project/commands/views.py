from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import ValidationError

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from commands.models import *
from rest_framework.response import Response
from commands.serializers import *
from commands.models import *
from commands.models import *


"""Categorie Manager class"""
class CategorieManagerView(viewsets.ModelViewSet):
    """Handle creating reading and updating Products"""

    authentication_classes = (TokenAuthentication,)
    serializer_class = CategorieManagerSerializer
    #permission_classes = (IsAuthenticated,permissions.IntentPermissions)
    def create(self, request, *args, **kwargs):
        print(self.request.data)
        verif={"success":True}
        serializer = CategorieManagerSerializer(data=self.request.data, context={'request': self.request})
        if serializer.is_valid():
            serializer.create(self.request.data)
            return Response({"sucess":"ok"})
        raise ValidationError(serializer.error_messages)

    def get_queryset(self):

        categories= Categories.objects.all()
        return (categories)



"""Product manager class"""
class ProductManagerView(viewsets.ModelViewSet):
    """Handle creating reading and updating Products"""

    #authentication_classes = (TokenAuthentication,)
    serializer_class = ProductManagerSerializer
    #permission_classes = (IsAuthenticated,permissions.IntentPermissions)
    def create(self, request, *args, **kwargs):
        print(self.request.data)
        verif={"success":True}
        serializer = ProductManagerSerializer(data=self.request.data, context={'request': self.request})
        if serializer.is_valid():
            serializer.create(self.request.data)
            return Response({"sucess":"ok"})
        raise ValidationError(serializer.error_messages)

    def get_queryset(self):

        products= Products.objects.all()
        return (products)


"""Commands manager class"""
class CommandsManagerView(viewsets.ModelViewSet):
    """Handle creating reading and updating Products"""

    #authentication_classes = (TokenAuthentication,)
    serializer_class = CommandsManagerSerializer
    #permission_classes = (IsAuthenticated,permissions.IntentPermissions)
    def create(self, request, *args, **kwargs):
        print(self.request.data)
        verif={"success":True}
        serializer = CommandsManagerSerializer(data=self.request.data, context={'request': self.request})
        if serializer.is_valid():
            serializer.create(self.request.data)
            return Response({"sucess":"ok"})
        raise ValidationError(serializer.error_messages)

    def get_queryset(self):

        commands= Commands.objects.all()
        return (commands)