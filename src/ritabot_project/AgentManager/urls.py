from django.urls import path, include
from AgentManager import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('agent', views.AgentManager, base_name='agent'),
router.register('defaultagent', views.AgentManager, base_name='default_agent'),
router.register('(?P<agentid>[0-9]+)/intents', views.IntentManagerView, base_name='intent')
router.register('(?P<agentid>[0-9]+)/adddefaultintents', views.AddDefaultIntentManagerView, base_name='add default intent')
router.register('(?P<agentName>[\w\-]+)/defaultintents', views.DefaultIntentManagerView, base_name='intent')
router.register('(?P<agentid>[0-9]+)/entity', views.EntityManagerView, base_name='Entity')
router.register('(?P<agentid>[0-9]+)/uploadvideo', views.VideoUploadManagerView, base_name='Video')
router.register('(?P<agentid>[0-9]+)/uploadaudio', views.AudioUploadManagerView, base_name='Audio')
router.register('(?P<intentid>[0-9]+)/(?P<agentid>[0-9]+)/outputcontext', views.OutputContextManagerView, base_name='outputcontext')
router.register('(?P<agentid>[0-9]+)/users', views.AgentCustomerManager, base_name='users')
router.register('agentinformations', views.GetAgentInfo, base_name='agentinfo')
# menu url
router.register('(?P<agentid>[0-9]+)/menu', views.MenuManagerView, base_name='menu')
# persistent menu permission for widget
router.register('(?P<agentid>[0-9]+)/menu_widget', views.GetMenuForWidget, base_name='menu_widget'),

urlpatterns = [
    path('', include(router.urls)),
    path('<int:agentid>/deletelanguage', views.Delete_Language.as_view()),
    path('launch_training', views.LaunchTraining.as_view()),
    path('test_training', views.TestTraining.as_view()),
    path('accepteinvit/<str:invitID>/', views.InvitationManager.as_view()),
    path('agent_status/<str:agentID>/', views.AgentStatusManager.as_view()),
    path('<int:agentid>/addquestions/', views.AddQuestionManagerView.as_view()),
    path('<int:agentid>/addlanguage/', views.AgentLanguageManager.as_view()),
    path('<int:agentid>/intents_export', views.ExportIntentManager.as_view()),
    path('<int:agentid>/intents_import', views.ImportIntentManager.as_view()),
    path('agents_export', views.ExportAgentsManager.as_view()),
    path('agents_import', views.ImportAgentsManager.as_view()),
    path('agent_restore', views.RestoreAgentManager.as_view()),
    path('stop_agent', views.Stop_Agent.as_view()),
    # persistent menu
    path('<int:agentid>/persistent_menu', views.PersistentMenuManagerView.as_view()),


]
