from django.db import models
import uuid
import os
from AgentManager.models import Agent
from django.utils import timezone



class Commentary(models.Model):

    client_id = models.CharField(max_length=256, null=True, blank=True)
    client = models.CharField(max_length=256, null=True, blank=True)
    gouvernorat = models.CharField(max_length=256, null=True, blank=True)
    region = models.CharField(max_length=256, null=True, blank=True)
    telephone = models.CharField(max_length=256, null=True, blank=True)

    data_creation = models.DateTimeField('creation Date', null=True)

    agent=models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='commentary_agent', blank=True, null=True)
    date_update = models.DateTimeField('update Date', null=True)


    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.data_creation = timezone.now()
        self.date_update = timezone.now()
        super(Commentary, self).save()
    def __str__(self):
        return self.client

class Commentary_Info(models.Model):
    besoin = models.CharField(max_length=256, null=True, blank=True)
    source = models.CharField(max_length=256, null=True, blank=True)
    data_contact = models.DateTimeField('Contact Date', null=True)
    commercial = models.CharField(max_length=256, null=True, blank=True)
    date_action = models.DateField('Action Date', null=True)
    observation = models.CharField(max_length=256, null=True, blank=True)
    prix = models.CharField(max_length=256, null=True, blank=True)
    remarque = models.TextField(blank=True, null=True, default="None")
    note = models.TextField(blank=True, null=True, default="None")
    Commentary = models.ForeignKey(Commentary, on_delete=models.CASCADE, related_name='commentary_info', blank=True, null=True)
    date_update = models.DateTimeField('update Date', null=True)
    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.data_contact = timezone.now()
        self.date_update = timezone.now()
        super(Commentary_Info, self).save()
    def __str__(self):
        return str(self.id)



