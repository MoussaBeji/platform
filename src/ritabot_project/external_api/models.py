from django.db import models
from django.utils import timezone
from AgentManager.models import Agent


class Student(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, blank=True, null=True,
                                       related_name='agent_students')
    first_name = models.CharField(max_length=128, null=True, blank=True ,default="Unknown")
    last_name = models.CharField(max_length=128, null=True, blank=True , default="Unknown")
    gender = models.CharField(max_length=128, null=True, blank=True ,default="Unknown")
    account_id = models.CharField(max_length=256, null=True, blank=True ,default="Unknown")
    email = models.EmailField(max_length=255) #email must be unique, unique=True
    phone_number = models.CharField(max_length=255, null=True)

    date_create = models.DateTimeField('Create Date', null=True)
    date_update = models.DateTimeField('Update Date', null=True, auto_now_add=True)


    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.date_create = timezone.now()
        self.date_update = timezone.now()
        super(Student, self).save()
    def __str__(self):
        return str(self.id)


class Formation(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, blank=True, null=True,
                                     related_name='agent_formations')
    formation = models.TextField(blank=True, null=True)
    date_create = models.DateTimeField('Create Date', null=True)
    date_update = models.DateTimeField('Update Date', null=True, auto_now_add=True)

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.date_create = timezone.now()
        self.date_update = timezone.now()
        super(Formation, self).save()

    def __str__(self):
        return str(self.formation)


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True, related_name='formations')
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, blank=True, null=True)
    date_create = models.DateTimeField('Create Date', null=True)
    date_update = models.DateTimeField('Update Date', null=True, auto_now_add=True)
    is_active = models.BooleanField(default=False)


    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.date_create = timezone.now()
        self.date_update = timezone.now()
        super(Enrollment, self).save()

    def __str__(self):
        return str(self.id)