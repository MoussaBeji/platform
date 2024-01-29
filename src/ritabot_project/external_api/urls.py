from django.urls import path, include
from external_api import views
from rest_framework.routers import DefaultRouter



router = DefaultRouter()
router.register('(?P<agentid>[0-9]+)/students', views.StudentEnrollmentView,base_name='student_enrollment')


urlpatterns = [
    path('', include(router.urls)),

]
