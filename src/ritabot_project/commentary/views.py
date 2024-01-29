from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import ValidationError

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from commentary.serializers import *
from .permissions import *
from commentary.models import *
from rest_framework.pagination import PageNumberPagination, BasePagination
from rest_framework import filters
from collections import OrderedDict
from rest_framework.renderers import JSONRenderer
from drf_renderer_xlsx.renderers import XLSXRenderer
from drf_renderer_xlsx.mixins import XLSXFileMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse



class exportcommentaryManagerView(APIView, XLSXRenderer):
    """Handle creating reading and updating Products"""

    authentication_classes = (TokenAuthentication,)
    #serializer_class = ExportCommentaryManagerSerializer
    permission_classes = (IsAuthenticated,default_permission)
    #renderer_classes = [JSONRenderer, XLSXRenderer, XLSXFileMixin]
    renderer_classes = (XLSXRenderer,)
    column_header = {
        'titles': [
            "Client",
            "Gouvernorat",
            "Région",
            "Téléphone",
            "Besoin",
            "Source",
            "Data de contact",
            "Commercial",
            "Date d'action",
            "Observation",
            "Prix",
            "Remarques",
            "Notes",
            "Dernier mise à jour",
        ],

        'height': 25,
        'style': {
             'fill': {
                'fill_type': 'solid',
                'start_color': '1f2540',
            },
            'alignment': {
                'horizontal': 'center',
                'vertical': 'center',
                'wrapText': True,
                'shrink_to_fit': True,
            },
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            },
            'font': {
                'name': 'Arial',
                'size': 12,
                'bold': True,
                'color': 'FFFFFF',
            },
        },
    }
    body = {
        'style': {

            'alignment': {
                'horizontal': 'center',
                'vertical': 'center',
                'wrapText': True,
                'shrink_to_fit': True,
            },
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            },
            'font': {
                'name': 'Arial',
                'size': 10,
                'bold': False,
                'color': 'FF000000',
            }
        },

    }

    def get( self, request, *args, **kwargs):
        agentid = self.kwargs['agentid']
        commantary= Commentary_Info.objects.filter(Commentary__agent=agentid).order_by('-data_contact')
        serializer = ExportCommentaryInfoManagerSerializer(commantary, many=True)
        res = Response(
            data=serializer.data
            , status=status.HTTP_200_OK
        )
        res['Content-Disposition'] = u'attachment; filename="users.xlsx"; content_type="application/xlsx"'
        return res




class StandardHistoriqueResultsSetPagination2(PageNumberPagination, BasePagination):
    page_size = 50000
    page_query_param="pageindex"
    page_size_query_param = 'pagesize'
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('totalCount', self.page.paginator.count),

            ('data', data)
        ]))




# Create your views here.
"""Product manager class"""
class commentaryManagerView(viewsets.ModelViewSet):
    """Handle creating reading and updating Products"""

    authentication_classes = (TokenAuthentication,)
    serializer_class = CommentaryManagerSerializer
    permission_classes = (IsAuthenticated,default_permission)
    pagination_class = StandardHistoriqueResultsSetPagination2
    filter_backends = (filters.SearchFilter,)
    search_fields = ('client_id', 'client', 'gouvernorat', 'region', 'telephone', 'data_creation')
    def create(self, request, *args, **kwargs):
        #print(self.request.data)
        verif={"success":True}
        serializer = CommentaryManagerSerializer(data=self.request.data, context={'request': self.request, 'agentid': self.kwargs['agentid']})
        if serializer.is_valid():
            serializer.create(self.request.data)
            return Response({"sucess":"ok"})
        raise ValidationError(serializer.error_messages)

    def get_queryset(self):
        agentid = self.kwargs['agentid']
        commantary= Commentary.objects.filter(agent=agentid).order_by('-data_creation')
        return (commantary)

