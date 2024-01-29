from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import ValidationError

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from collections import OrderedDict

from analytics import models, permissions
from rest_framework.response import Response
from analytics.serializers import *
from analytics.models import *
from AgentManager.models import *
from rest_framework.pagination import PageNumberPagination, BasePagination
from rest_framework import filters
from datetime import date, timedelta
from rest_framework.views import APIView, View

"""     Define the pagination class for analytics"""
class StandardHistoriqueResultsSetPagination(PageNumberPagination, BasePagination):
    page_size = 50000
    page_query_param="pageindex"
    page_size_query_param = 'pagesize'
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('totalCount', self.page.paginator.count),

            ('Historique', data)
        ]))

class StandardHistoriqueResultsSetPagination2(PageNumberPagination, BasePagination):
    page_size = 50000
    page_query_param="pageindex"
    page_size_query_param = 'pagesize'
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response(data)


#Filter

# from rest_framework.filters import DateRangeFilter,DateFilter
# from wesapp.models import MyModel
#
# class SaleItemFilter(django_filters.FilterSet):
#     start_date = DateFilter(name='date',lookup_type=('gt'),)
#     end_date = DateFilter(name='date',lookup_type=('lt'))
#     date_range = DateRangeFilter(name='date')
#
#     class Meta:
#         model = SaleItem
#         fields = ['entered_by',]

#End filter


class AnalyticsManagerView(viewsets.ModelViewSet):
    """Handling the analytics viewset manager"""

    authentication_classes = (TokenAuthentication,)
    serializer_class = AnalyticsSerializer
    queryset = AgentStats.objects.all()
    pagination_class = StandardHistoriqueResultsSetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('platform', 'chaine')
    permission_classes = ( IsAuthenticated, permissions.AnalyticsPermissions,)

    def create(self, request, *args, **kwargs):

        serializer = AnalyticsSerializer(data=request.data, context={'request': self.request, 'agentid': self.kwargs['agentid']})

        if serializer.is_valid():
            agentStats = serializer.save()
            return Response({"success": True})
        raise ValidationError(serializer.error_messages)
        #comment
    # def getdaysrange(self, startdate, enddate):
    #     styear, stmonth, stday = startdate.split('-')
    #     enyear, enmonth, enday = enddate.split('-')
    #     from datetime import date, timedelta
    #     stdate = date(int(styear), int(stmonth), int(stday))
    #     endate = date(int(enyear), int(enmonth), int(enday))
    #     delta = endate - stdate
    #     rangedays = []
    #     for i in range(delta.days + 1):
    #         rangedays.append(str(stdate + timedelta(days=i)))
    #     return rangedays
    def get_queryset(self):
        agentid = self.kwargs['agentid']
        if self.request.query_params.get('startdate', None) and self.request.query_params.get('enddate', None):
            startdate = datetime.strptime(self.request.query_params.get('startdate', None), '%Y-%m-%d')
            enddate = datetime.strptime(self.request.query_params.get('enddate', None), '%Y-%m-%d')
        else:
            startdate = date.today() - timedelta(days=180)
            enddate = date.today()

        perm = UserPermissions.objects.filter(user_profile=self.request.user, is_active=True).values('agent')
        agent = Agent.objects.filter(id__in=perm).values('id')

        if any(a['id'] == int(agentid) for a in agent):
            if startdate and enddate:
                agentStat=AgentStats.objects.filter(agent=agentid, endTime__range=(startdate, enddate+timedelta(days=1))).order_by('-id')
            else:
                agentStat=AgentStats.objects.filter(agent=agentid, endTime__range=(startdate, enddate+timedelta(days=1))).order_by('-id')
        else:
            agentStat=None
        if 'pageindex' in self.request.get_full_path() or 'pagesize' in self.request.get_full_path():
            self.pagination_class = StandardHistoriqueResultsSetPagination
        else:
            self.pagination_class = StandardHistoriqueResultsSetPagination2

        return (agentStat)



class UsersManagerView(viewsets.ModelViewSet):
    """Handling the analytics viewset manager"""

    authentication_classes = (TokenAuthentication,)
    serializer_class = UsersManagerSerializer
    queryset = InfoUser.objects.all()
    #pagination_class = StandardHistoriqueResultsSetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('client_id',)
    permission_classes = ( IsAuthenticated, permissions.UserinfoPermissions,)

    def update(self, request, *args, **kwargs):

        data = self.request.data
        try:
            externalinfo = data.get('external_info')
            print(externalinfo)
        except:
            raise serializers.ValidationError({'Erreur': [_("vous devez envoyer des donn�es JSON sous cette format external_info:...JSON...")]})

        instance = self.get_object()
        info=instance.external_info
        if not info:
            objinfo=ExternalInfo.objects.create(
                payload=json.dumps(externalinfo)

            )
            instance.external_info=objinfo
            instance.save()
        else:
            info.payload=json.dumps(externalinfo)
            info.save()

        return Response({"sucess": "ok"})
    def get_queryset(self):
        agentid = self.kwargs['agentid']
        Info = InfoUser.objects.filter(agent=agentid)
        return Info

class UserAnalyticsManagerView(viewsets.ModelViewSet):
    """Handling the analytics viewset manager"""

    authentication_classes = (TokenAuthentication,)
    serializer_class = UserAnalyticsSerializer
    queryset = InfoUser.objects.all()
    pagination_class = StandardHistoriqueResultsSetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('client_id', 'gender')
    permission_classes = ( IsAuthenticated, permissions.AnalyticsPermissions,)

    def create(self, request, *args, **kwargs):

        serializer = UserAnalyticsSerializer(data=request.data, context={'request': self.request, 'agentid': self.kwargs['agentid']})

        if serializer.is_valid():
            agentStats = serializer.save()
            return Response({"success": True})
        raise ValidationError(serializer.error_messages)

    def get_queryset(self):
        agentid = self.kwargs['agentid']
        if self.request.query_params.get('startdate', None) and self.request.query_params.get('enddate', None):
            startdate = datetime.strptime(self.request.query_params.get('startdate', None), '%Y-%m-%d')
            enddate = datetime.strptime(self.request.query_params.get('enddate', None), '%Y-%m-%d')
        else:
            startdate = date.today() - timedelta(days=180)
            enddate = date.today()

        perm = UserPermissions.objects.filter(user_profile=self.request.user, is_active=True).values('agent')
        agent = Agent.objects.filter(id__in=perm).values('id')

        if any(a['id'] == int(agentid) for a in agent):
            if startdate and enddate:

                agentStat=AgentStats.objects.filter(agent=agentid, endTime__range=(startdate, enddate+timedelta(days=1))).order_by('-id').values('agent')
            else:
                agentStat=AgentStats.objects.filter(agent=agentid, endTime__range=(startdate, enddate+timedelta(days=1))).order_by('-id').values('info_user')
        else:
            agentStat=None
        Info = InfoUser.objects.filter(agent=agentid)
        if 'pageindex' in self.request.get_full_path() or 'pagesize' in self.request.get_full_path():
            self.pagination_class = StandardHistoriqueResultsSetPagination
        else:
            self.pagination_class = StandardHistoriqueResultsSetPagination2

        return (Info)


class get_path(APIView):

    def get(self, request, *args, **kwargs):
        import os
        return Response({"path": str(os.getcwd())})
