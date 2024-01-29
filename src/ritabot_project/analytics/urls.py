from django.urls import path, include
from analytics.views import *
from rest_framework.routers import DefaultRouter



router = DefaultRouter()
router.register('(?P<agentid>[0-9]+)/analytics', AnalyticsManagerView, base_name='AnalyticsManagerView')
router.register('(?P<agentid>[0-9]+)/analyticbyusers', UserAnalyticsManagerView, base_name='AnalyticsManagerView_Byuser')
router.register('(?P<agentid>[0-9]+)/getuserinfo', UsersManagerView, base_name='GetUserInfo')

urlpatterns = [
    path('', include(router.urls)),
    path('get_path/', get_path.as_view(), name='getpath'),

]
