from rest_framework.response import Response
from rest_framework import serializers, fields
from datetime import datetime
from AgentManager.models import *
from ProfileManager.models import *
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.contrib.auth import authenticate
from operator import itemgetter
from rest_framework.serializers import ReadOnlyField, EmailField
from rest_framework.exceptions import ValidationError
from django.db.models.fields import TextField

from ritabot.settings import *

""" For sending email and hash the user ID import the following custumized packages """
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
"""     End importing send email packages    """
import base64
from django.core.files.base import ContentFile


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['name', 'order']


class RandomTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = RandomText
        fields = ['name', 'order']


class SimpleResponseSerializer(serializers.ModelSerializer):
    random_text_set = RandomTextSerializer(many=True, required=False)

    class Meta:
        model = SimpleResponse
        fields = ['random_text_set']


class ButtonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Button
        fields = ['name', 'url', 'payload', 'order']


class TextResponseSerializer(serializers.ModelSerializer):
    button_set = ButtonSerializer(many=True, required=False)

    class Meta:
        model = TextResponse
        fields = ['name', 'order', 'button_set']


class SliderSerializer(serializers.ModelSerializer):
    button_set = ButtonSerializer(many=True, required=False)
    imageName = serializers.SerializerMethodField('get_imageName')

    class Meta:
        model = Slider
        fields = ['imageName', 'title', 'subtitle', 'url', 'order', 'button_set']

    def get_imageName(self, obj):

        image_name = obj.imagename()
        return image_name


class GallerySerializer(serializers.ModelSerializer):
    slider_set = SliderSerializer(many=True)

    class Meta:
        model = Gallery
        fields = ['order', 'slider_set']


class QuickReplySerializer(serializers.ModelSerializer):
    button_set = ButtonSerializer(many=True)

    class Meta:
        model = QuickReply
        fields = ['name', 'order', 'button_set']


class ImageSerializer(serializers.ModelSerializer):
    imageName = serializers.SerializerMethodField('get_imageName')

    class Meta:
        model = Image
        fields = ['order', 'imageName']

    def get_imageName(self, obj):

        image_name = obj.imagename()
        return image_name


class MixedResponseSerializer(serializers.ModelSerializer):
    text_response_set = TextResponseSerializer(many=True, required=False)
    gallery_set = GallerySerializer(many=True, required=False)
    quick_reply_set = QuickReplySerializer(many=True, required=False)
    image_set = ImageSerializer(many=True, required=False)

    class Meta:
        model = MixedResponse
        fields = ['text_response_set', 'gallery_set', 'quick_reply_set', 'image_set']


class BlockResponseSerializer(serializers.ModelSerializer):
    simple_response_set = SimpleResponseSerializer(many=True, required=False)
    mixed_response_set = MixedResponseSerializer(many=True, required=False)

    def get_nb(self, obj):
        return obj.mixed_response.count()

    class Meta:
        model = BlockResponse
        fields = ['is_complex', 'simple_response_set', 'mixed_response_set']

        # def get_fields(self):
        #     if self.simple_response_set.count() > 0:
        #
        #         return ['simple_response_set']
        #     else:
        #         return ['mixed_response_set']
        #
        # fields = get_fields(self)




class OutputContextSerializer(serializers.ModelSerializer):

    class Meta:
        model = OutputContext
        fields = ['outContext']


class InputContextSerializer(serializers.ModelSerializer):
    Outname = serializers.CharField(source='outContext.outContext', required=False)
    #outContextID = serializers.SerializerMethodField('get_outContextID')

    class Meta:
        model = InputContext
        fields = ["Outname"]

    def get_outContextID(self, obj):
        return obj.outContext.id



class IntentAudioManagerSerializer(serializers.ModelSerializer):
    # url = serializers.CharField(source='audio.audio.name')
    audio = serializers.SerializerMethodField('get_audio_name')

    class Meta:
        model = Audio_Intent
        fields = ['audio']

    def get_audio_name(self, obj):

        audio_name = obj.audio.audioname()
        return audio_name

class IntentVideoManagerSerializer(serializers.ModelSerializer):
    video = serializers.SerializerMethodField('get_video_name')
    class Meta:
        model = Video_Intent
        fields = ['video']

    def get_video_name(self, obj):

        video_name = obj.video.videoname()
        return video_name


class Entity_SynonymeManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Synonyme
        fields = ['synonyme']

class Entity_ValueManagerSerializer(serializers.ModelSerializer):
    synonyme_set = Entity_SynonymeManagerSerializer(many=True, required=False)
    class Meta:
        model = Value
        fields = ['value', 'synonyme_set']

class EntityManagerSerializer(serializers.ModelSerializer):
    value_set = Entity_ValueManagerSerializer(many=True, required=False)
    class Meta:
        model = Entity
        fields = ['name', 'is_default', 'value_set']


class IntentEntityManagerSerializer(serializers.ModelSerializer):
    entity = EntityManagerSerializer(many=False, required = True)
    class Meta:
        model = Entity_Intent
        fields = ['entity', 'prompt_response', 'is_required']



class IntentManagerSerializer(serializers.ModelSerializer):
    question_set = QuestionSerializer(many=True, required=False)
    block_response_set = BlockResponseSerializer(many=True, required=False)
    output_context_set = OutputContextSerializer(many=True, required=False)
    input_context_set = InputContextSerializer(many=True, required=False)
    related_audios = IntentAudioManagerSerializer(many=True, required=False)
    related_audioExportTranslate = related_audios
    related_videos = IntentVideoManagerSerializer(many=True, required=False)
    related_videoExportTranslate = related_videos
    related_entity = IntentEntityManagerSerializer(many=True, required=False)
    related_entityExportTranslate = related_entity
    class Meta:
        model = Intent
        fields = ['name', 'description', 'is_active', 'is_none_response', 'is_depart', 'question_set', 'block_response_set', 'output_context_set', 'input_context_set',
                  'related_audios', 'related_videos', 'related_entity', 'related_entityExportTranslate', 'related_audioExportTranslate',
                  'related_videoExportTranslate']
        extra_kwargs = {
            'agent': {'read_only': True, 'required': True},
        }


class AgentManagerSerializer(serializers.ModelSerializer):
    """Serialize class for Agent"""
    #intent_set = IntentManagerSerializer(many=True, required=False)
    intent_set = serializers.SerializerMethodField('get_intentList')
    imageName = serializers.SerializerMethodField('get_imageName')

    class Meta:
        model = Agent
        fields = ['name', 'description', 'language', 'time_zone', 'imageName', 'port', 'status', 'intent_set']
        extra_kwargs = {
            'port': {'read_only': True},
            'status': {'read_only': True},
            'image': {'required': False}

        }

    def get_intentList(self, instance):
        intent = Intent.objects.filter(agent=instance).order_by('-date_update').reverse()
        return IntentManagerSerializer(intent, many=True).data

    def get_imageName(self, obj):
        image_name = obj.imagename()
        return image_name