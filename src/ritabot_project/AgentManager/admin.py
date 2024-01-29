from django.contrib import admin
from .models import *

class UserPermissionsAdmin(admin.ModelAdmin):
    list_display = ('id','user_profile', 'agent', 'is_admin', 'is_active')
    list_display_links = ('id', 'user_profile')
    list_per_page = 25


class IntentAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'agent', 'date_create')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    list_per_page = 25

class AgentAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'language', 'date_update')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    list_per_page = 25





admin.site.register(Intent,IntentAdmin)
admin.site.register(Agent,AgentAdmin)
admin.site.register(UserPermissions, UserPermissionsAdmin)

admin.site.register(BlockResponse)
admin.site.register(MixedResponse)
admin.site.register(Image)
admin.site.register(Gallery)
admin.site.register(Slider)
admin.site.register(Button)
admin.site.register(QuickReply)
admin.site.register(Question)
admin.site.register(TextResponse)
admin.site.register(InputContext)
admin.site.register(OutputContext)
admin.site.register(SimpleResponse)
admin.site.register(RandomText)
admin.site.register(Entity)
admin.site.register(Value)
admin.site.register(Synonyme)
admin.site.register(Entity_Intent)
admin.site.register(Video)
admin.site.register(Video_Intent)
admin.site.register(Audio)
admin.site.register(Audio_Intent)
admin.site.register(Menu)
admin.site.register(Related_Agent)
admin.site.register(NavigationIntent)
admin.site.register(DependingNavigation)
