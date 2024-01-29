from django.contrib import admin

# Register your models here.
from commands.models import *
admin.site.register(Categories)
admin.site.register(Products)
admin.site.register(Commands)
