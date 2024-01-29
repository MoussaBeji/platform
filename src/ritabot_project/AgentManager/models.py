from django.db import models
from datetime import datetime
from django.conf import settings
import uuid
from django.utils import timezone
import os
import shutil #import for image

class HasFileQuerySet(models.QuerySet):
    """Overwrite the function for deleting all contents of file/image field"""

    def delete(self, *args, **kwargs):

        for obj in self:
            if hasattr(obj, 'video'):
                obj.video.delete()
            if hasattr(obj, 'image'):
                obj.image.delete()
            if hasattr(obj, 'audio'):
                obj.audio.delete()
        super(HasFileQuerySet, self).delete(*args, **kwargs)


def filePath(instance, filename):
    """Generate file path for new mage/file"""

    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('upoloads/file/', filename)


def imageFilePath(instance, filename):
    """Generate file path for new mage/file"""

    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('upoloads/image/', filename)

def VideoFilePath(instance, filename):
    """Generate file path for new mage/file"""

    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('upoloads/video/', filename)

def AudioFilePath(instance, filename):
    """Generate file path for new mage/file"""

    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('upoloads/audio/', filename)

class Related_Agent(models.Model):
    """Created with each creation of new agent to differentiate the agent groups"""
    name = models.TextField(blank=False, null=False, default="default_name")

    def __str__(self):
        return str(self.id)

class Agent(models.Model):
    objects = HasFileQuerySet.as_manager()
    name = models.CharField(max_length=32)
    language = models.CharField(max_length=32, default="Francais")
    time_zone = models.CharField(max_length=32, default='GMT +1')
    status = models.CharField(default='Non entraîné', max_length=1000)
    date_create = models.DateTimeField('Create Date', null=True)
    date_update = models.DateTimeField('Update Date', null=True, auto_now_add=True)
    image = models.ImageField(default='upoloads/image/65ca9c88-115d-4837-b24f-75046046cbc0.png', null=True, upload_to=imageFilePath)
    port = models.IntegerField(null=True)
    description = models.TextField(blank=True, null=True)
    is_default = models.BooleanField(default=False)
    is_main = models.BooleanField(default=True)
    related_agent = models.ForeignKey(
        Related_Agent,
        on_delete=models.CASCADE,
        related_name='agents',
        null=True, blank=True
    )
    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.date_create = timezone.now()
        self.date_update = timezone.now()
        return super(Agent, self).save()
    def delete(self, using=None, keep_parents=False):
        try:
            os.remove(self.image.path)
        except:
            pass
        Agent.objects.filter(id = self.id).delete()


    def imagename(self):
        return os.path.basename(self.image.name)

    def __str__(self):
        return self.name

class UserPermissions(models.Model):
    user_profile = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='userinfo',
    )
    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='permission'
    )
    is_admin=models.BooleanField(default=False)
    creating_access=models.BooleanField(default=False)
    reading_access=models.BooleanField(default=False)
    updating_access=models.BooleanField(default=False)
    deleting_access=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.user_profile.username



class Intent(models.Model):
    name = models.TextField(blank=False, null=False, default="default_name")
    date_create = models.DateTimeField('Create Date', null=True)
    date_update = models.DateTimeField('Update Date', null=True, auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    fulfillment = models.TextField(blank=True, null=True)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, blank=False, null=True)
    is_depart = models.BooleanField(default=False)
    is_none_response = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.date_create = timezone.now()
            self.date_update = timezone.now()
        self.agent.status = "Non entraîné"
        self.agent.save()
        super(Intent, self).save()

    def delete(self, *args, **kwargs):
        self.agent.status = "Non entraîné"
        self.agent.save()
        #super(Intent, self).save()
        super(Intent, self).delete(*args, **kwargs)


    def __str__(self):
        return str(self.id)

###############     Navigation intent      ##################
class NavigationIntent(models.Model):
    nb_tentative=models.IntegerField(default=1)
    redirection = models.ForeignKey(Intent, on_delete=models.CASCADE, blank=False, null=False, related_name='redirection_intent')
    echec = models.ForeignKey(Intent, on_delete=models.CASCADE, blank=False, null=False, related_name='echec_intent')
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, blank=False, null=False, related_name='related_navigation')

    def __str__(self):
        return str(self.id)

class DependingNavigation(models.Model):
    nav_intent = models.ForeignKey(NavigationIntent, on_delete=models.CASCADE, blank=True, null=False, related_name='related_depending')
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, blank=True, null=False, related_name='depending_intent')

    def __str__(self):
        return str(self.nav_intent)

class OutputContext(models.Model):
    date_create = models.DateTimeField('Create Date', null=True)
    date_update = models.DateTimeField('Update Date', null=True, auto_now_add=True)
    outContext = models.TextField(blank=False, null=False)
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, blank=True, null=False,
                               related_name='output_context_set')
    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.date_create = timezone.now()
        self.date_update = timezone.now()
        super(OutputContext, self).save()
    def __str__(self):
        return self.outContext


class InputContext(models.Model):
    date_create = models.DateTimeField('Create Date', null=True)
    date_update = models.DateTimeField('Update Date', null=True, auto_now_add=True)
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, blank=True, null=False,
                               related_name='input_context_set')
    outContext = models.ForeignKey(OutputContext, on_delete=models.CASCADE, blank=True, null=False,
                                   related_name='out_Context')
    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.date_create = timezone.now()
        self.date_update = timezone.now()
        super(InputContext, self).save()
    def __str__(self):
        return str(self.id)


class Question(models.Model):
    name = models.CharField(max_length=300, blank=False, null=True)
    date_create = models.DateTimeField('Create Date', null=True)
    date_update = models.DateTimeField('Update Date', null=True, auto_now_add=True)
    order = models.IntegerField(null=True)
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, blank=True, null=False, related_name='question_set')

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.date_create = timezone.now()
        self.date_update = timezone.now()
        super(Question, self).save()

    def __str__(self):
        return self.name


class BlockResponse(models.Model):
    date_create = models.DateTimeField('Create Date', null=True)
    date_update = models.DateTimeField('Update Date', null=True, auto_now_add=True)
    is_complex = models.BooleanField(null=False, blank=True)
    category = models.TextField(blank=True, null=True, default="default")
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, blank=True, null=False,
                               related_name='block_response_set')

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.date_create = timezone.now()
        self.date_update = timezone.now()
        super(BlockResponse, self).save()

    def __str__(self):
        return str(self.id)


class SimpleResponse(models.Model):
    date_create = models.DateTimeField('Create Date', null=True)
    date_update = models.DateTimeField('Update Date', null=True, auto_now_add=True)
    block_response = models.ForeignKey(BlockResponse, on_delete=models.CASCADE, blank=True, null=False,
                                       related_name='simple_response_set')

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.date_create = timezone.now()
        self.date_update = timezone.now()
        super(SimpleResponse, self).save()

    def __str__(self):
        return str(self.id)


class RandomText(models.Model):
    name = models.TextField(blank=True, null=True)
    date_create = models.DateTimeField('Create Date', null=True)
    date_update = models.DateTimeField('Update Date', null=True, auto_now_add=True)
    simple_response = models.ForeignKey(SimpleResponse, on_delete=models.CASCADE, blank=True, null=False,
                                        related_name='random_text_set')
    order = models.IntegerField(blank=True, null=False)

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.date_create = timezone.now()
        self.date_update = timezone.now()
        super(RandomText, self).save()

    def __str__(self):
        return self.name


class MixedResponse(models.Model):
    date_create = models.DateTimeField('Create Date', null=True)
    date_update = models.DateTimeField('Update Date', null=True, auto_now_add=True)
    block_response = models.ForeignKey(BlockResponse, on_delete=models.CASCADE, blank=True, null=False,
                                       related_name='mixed_response_set')

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.date_create = timezone.now()
        self.date_update = timezone.now()
        super(MixedResponse, self).save()

    def __str__(self):
        return str(self.id)


class TextResponse(models.Model):
    name = models.TextField(blank=True, null=True)
    date_create = models.DateTimeField('Create Date', null=True)
    date_update = models.DateTimeField('Update Date', null=True, auto_now_add=True)
    mixed_response = models.ForeignKey(MixedResponse, on_delete=models.CASCADE, blank=False, null=False,
                                       related_name='text_response_set')
    order = models.IntegerField(blank=True)

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.date_create = timezone.now()
        self.date_update = timezone.now()
        super(TextResponse, self).save()

    def __str__(self):
        return self.name


class Gallery(models.Model):
    date_create = models.DateTimeField('Create Date', null=True)
    date_update = models.DateTimeField('Update Date', null=True, auto_now_add=True)
    mixed_response = models.ForeignKey(MixedResponse, on_delete=models.CASCADE, blank=True, null=False,
                                       related_name='gallery_set')
    order = models.IntegerField(blank=True)

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.date_create = timezone.now()
        self.date_update = timezone.now()
        super(Gallery, self).save()

    def __str__(self):
        return str(self.id)



class Slider(models.Model):
    objects = HasFileQuerySet.as_manager()
    image = models.ImageField(upload_to=imageFilePath, blank=True, null=True)
    # image = models.TextField(blank=False, null=True)
    title = models.CharField(max_length=250, blank=True)
    subtitle = models.CharField(max_length=250, blank=True, null=True)
    url = models.CharField(max_length=250, blank=True, null=True)
    date_create = models.DateTimeField('Create Date', null=True)
    date_update = models.DateTimeField('Update Date', null=True, auto_now_add=True)
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, null=False, blank=True, related_name='slider_set')
    order = models.IntegerField(blank=True)

    def imagename(self):
        return os.path.basename(self.image.name)

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.date_create = timezone.now()
        self.date_update = timezone.now()
        super(Slider, self).save()

    def delete(self, using=None, keep_parents=False):
        try:
            os.remove(self.image.path)
        except:
            pass
        Slider.objects.filter(id = self.id).delete()

    def __str__(self):
        return str(self.id)


class QuickReply(models.Model):
    name = models.TextField(blank=True)
    date_create = models.DateTimeField('Create Date', null=True)
    date_update = models.DateTimeField('Update Date', null=True, auto_now_add=True)
    mixed_response = models.ForeignKey(MixedResponse, on_delete=models.CASCADE, blank=True, null=False,
                                       related_name='quick_reply_set')
    order = models.IntegerField(blank=True)

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.date_create = timezone.now()
        self.date_update = timezone.now()
        super(QuickReply, self).save()

    def __str__(self):
        return self.name


class Image(models.Model):
    objects = HasFileQuerySet.as_manager()
    image = models.ImageField(upload_to=imageFilePath, blank=True, null=True)
    date_create = models.DateTimeField('Create Date', null=True)
    date_update = models.DateTimeField('Update Date', null=True, auto_now_add=True)
    mixed_response = models.ForeignKey(MixedResponse, on_delete=models.CASCADE, blank=True, null=False,
                                       related_name='image_set')
    order = models.IntegerField(blank=True)

    def imagename(self):
        return os.path.basename(self.image.name)

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.date_create = timezone.now()
        self.date_update = timezone.now()
        super(Image, self).save()

    def delete(self, using=None, keep_parents=False):
        try:
            os.remove(self.image.path)
        except:
            pass
        Image.objects.filter(id = self.id).delete()

    def __str__(self):
        return str(self.id)


class Menu(models.Model):
    name = models.TextField(blank=False, null=False, default="default_name")
    date_create = models.DateTimeField('Create Date', null=True)
    date_update = models.DateTimeField('Update Date', null=True, auto_now_add=True)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, blank=False, null=True)
    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.date_create = timezone.now()
        self.date_update = timezone.now()
        super(Menu, self).save()
    def __str__(self):
        return self.name

class Button(models.Model):
    name = models.CharField(max_length=60, null=False, blank=True)
    url = models.URLField(max_length=250, null=True, blank=True)
    payload = models.CharField(max_length=1000, null=True, blank=True)
    phone_number = models.CharField(max_length=1000, null=True, blank=True)
    messenger_extensions = models.BooleanField(default=True)
    slider = models.ForeignKey(Slider, on_delete=models.CASCADE, null=True, blank=True,
                               related_name='button_set')
    quick_reply = models.ForeignKey(QuickReply, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='button_set')
    text_response = models.ForeignKey(TextResponse, on_delete=models.CASCADE, null=True, blank=True,
                                      related_name='button_set')
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, null=True, blank=True,
                                      related_name='button_set')
    sub_menu = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True,
                                      related_name='button_set')
    date_create = models.DateTimeField('Create Date', null=True)
    date_update = models.DateTimeField('Update Date', null=True, auto_now_add=True)
    order = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=40, null=True, blank=True)
    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.date_create = timezone.now()
        self.date_update = timezone.now()
        super(Button, self).save()
    def __str__(self):
        return self.name


###############     Video/audio      ##################



class Video(models.Model):
    objects = HasFileQuerySet.as_manager()
    video = models.FileField(upload_to=VideoFilePath, blank=True, null=True)
    date_create = models.DateTimeField('Create Date', null=True)
    date_update = models.DateTimeField('Update Date', null=True, auto_now_add=True)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, blank=True, null=False, related_name='video_agent')

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.date_create = timezone.now()
        self.date_update = timezone.now()
        super(Video, self).save()


    def get_url(self):
        return self.video.url

    def videoname(self):
        return os.path.basename(self.video.name)

    def __str__(self):
        return str(self.video)


class Video_Intent(models.Model):
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, blank=True, null=True, related_name='related_videos')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, blank=True, null=True, related_name='videos')

    def __str__(self):
        return str(self.id)

class Audio(models.Model):
    objects = HasFileQuerySet.as_manager()
    audio = models.FileField(upload_to=AudioFilePath, blank=True, null=True)
    date_create = models.DateTimeField('Create Date', null=True)
    date_update = models.DateTimeField('Update Date', null=True, auto_now_add=True)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, blank=True, null=False, related_name='audio_agent')
    #Add entity params here!
    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.date_create = timezone.now()
        self.date_update = timezone.now()
        super(Audio, self).save()

    def audioname(self):
        return os.path.basename(self.audio.name)

    def __str__(self):
        return self.audio


class Audio_Intent(models.Model):
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, blank=True, null=True, related_name='related_audios')
    audio = models.ForeignKey(Audio, on_delete=models.CASCADE, blank=True, null=True, related_name='audios')

    def __str__(self):
        return str(self.id)


###############     ENTITY      ##################

class Entity(models.Model):

    name = models.CharField(max_length=300, blank=False, null=True)
    date_create = models.DateTimeField('Create Date', null=True)
    date_update = models.DateTimeField('Update Date', null=True, auto_now_add=True)
    is_default =models.BooleanField(default=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, blank=True, null=False, related_name='agent')
    #Add entity params here!
    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.date_create = timezone.now()
        self.date_update = timezone.now()
        super(Entity, self).save()

    def __str__(self):
        return self.name

class Value(models.Model):
    value = models.CharField(max_length=300, blank=False, null=True)
    date_create = models.DateTimeField('Create Date', null=True)
    date_update = models.DateTimeField('Update Date', null=True, auto_now_add=True)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, blank=True, null=False, related_name='value_set')

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.date_create = timezone.now()
        self.date_update = timezone.now()
        super(Value, self).save()

    def __str__(self):
        return self.value


class Synonyme(models.Model):
    synonyme = models.CharField(max_length=300, blank=False, null=True)
    date_create = models.DateTimeField('Create Date', null=True)
    date_update = models.DateTimeField('Update Date', null=True, auto_now_add=True)
    value = models.ForeignKey(Value, on_delete=models.CASCADE, blank=True, null=True, related_name='synonyme_set')

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.date_create = timezone.now()
        self.date_update = timezone.now()
        super(Synonyme, self).save()

    def __str__(self):
        return self.synonyme

class Entity_Intent(models.Model):
    prompt_response = models.CharField(max_length=500, blank=True, null=True)
    is_required =models.BooleanField(default=False)
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, blank=True, null=True, related_name='related_entity')
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, blank=True, null=True, related_name='entity')

    def __str__(self):
        return str(self.id)

