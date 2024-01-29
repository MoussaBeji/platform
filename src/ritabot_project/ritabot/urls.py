from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

"""Include the urls defined at each created app"""
urlpatterns = [

    path('admin/', admin.site.urls),
    path('api/', include('ProfileManager.urls')),
    path('api/bot/', include('AgentManager.urls')),
    path('api/stats/', include('analytics.urls')),
    path('api/scom/', include('commentary.urls')), #SCOM-solaire
    path('api/external/', include('external_api.urls')),
    #path('api/commands/', include('commands.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
