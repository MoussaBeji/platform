from django.db import models
from datetime import datetime
from django.conf import settings
import uuid
from django.utils import timezone
from AgentManager.models import Agent, Intent
import os

class ExternalInfo(models.Model):
    #echeance = models.BooleanField(default=False)
    payload = models.TextField(blank=True, null=True, default="{}")
    #last_notification_date = models.DateTimeField('last_notification_date', null=True, blank=True)
    def __str__(self):
        return str(self.id)

class InfoUser(models.Model):
    first_name = models.CharField(max_length=128, null=True, blank=True ,default="Unknown")
    last_name = models.CharField(max_length=128, null=True, blank=True , default="Unknown")
    gender = models.CharField(max_length=128, null=True, blank=True ,default="Unknown")
    client_id = models.CharField(max_length=256, null=True, blank=True ,default="Unknown")
    page_id = models.CharField(max_length=256, null=True, blank=True ,default="Unknown")
    access_token = models.TextField(blank=True, null=True, default="None")
    creation_date= models.DateTimeField('creation Date', null=True, auto_now_add=True)
    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='Agent_user',
        null=True

    )
    external_info = models.ForeignKey(
        ExternalInfo,
        on_delete=models.SET_DEFAULT,
        related_name='external_info',
        null=True,
        blank=True,
        default=None

    )

    def __str__(self):
        return self.client_id

class AgentStats(models.Model):

    sessionID = models.CharField(max_length=128, null=True)
    chaine = models.CharField(max_length=128, default="Site Web professionel", null=True)
    adresseIP = models.CharField(max_length=128, default="Inconnue", null=True)
    country = models.CharField(max_length=128, default="Inconnue", null=True)
    platform = models.CharField(max_length=128, default="Inconnue", null=True)
    browser = models.CharField(max_length=128, default="Inconnue", null=True)
    startTime = models.DateTimeField('Update Date', null=True, auto_now_add=True)
    endTime = models.DateTimeField('Update Date', null=True, auto_now_add=True)
    info_user = models.ForeignKey(
        InfoUser,
        on_delete=models.CASCADE,
        related_name='sessions',
        null=True,
        blank=True

    )

    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='Agent',

    )

    def __str__(self):
        return self.sessionID

class Conversation(models.Model):

    inputMsg = models.TextField(blank=True, null=True, default="None")
    outputIntent=models.ForeignKey(Intent, on_delete=models.CASCADE, related_name='outputIntent', blank=True, null=True)
    outputRate= models.CharField(max_length=250, blank=True, null=True)
    date = models.DateTimeField(null=True, auto_now_add=True)
    agentStats=models.ForeignKey(AgentStats, on_delete=models.CASCADE, related_name='agentStats', null=True)


    def __str__(self):
        return self.inputMsg
