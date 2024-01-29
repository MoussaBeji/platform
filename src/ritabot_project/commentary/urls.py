from django.urls import path, include
from commentary import views
from rest_framework.routers import DefaultRouter



router = DefaultRouter()

router.register('(?P<agentid>[0-9]+)/commentary', views.commentaryManagerView,base_name='commentarylist')


urlpatterns = [
    path('', include(router.urls)),
    path('<int:agentid>/exportinfo/', views.exportcommentaryManagerView.as_view()),

]