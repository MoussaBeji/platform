from rest_framework.response import Response
from rest_framework import serializers, fields
from datetime import datetime

from AgentManager import export_serializers
from AgentManager.models import *
from ProfileManager.models import *
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.contrib.auth import authenticate
from operator import itemgetter
from rest_framework.serializers import ReadOnlyField, EmailField
from rest_framework.exceptions import ValidationError
from django.db.models.fields import TextField
"""inspect to know the class name"""
import inspect
from ritabot.settings import *
from io import BytesIO
""" For sending email and hash the user ID import the following custumized packages """
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
"""     End importing send email packages    """
import base64
from django.core.files.base import ContentFile

""" os """
import os

""" import File package """
from django.core.files import File


#####################   Audio/Video    #####################

class UploadVideoManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'video', 'date_create']
        extra_kwargs = {
            'date_create': {'read_only': True, 'required': False},
            #'date_update': {'read_only': True, 'required': False},
        }
    def create(self, validated_data):
        video = validated_data['video']
        agent = self.context['agentid']
        try:
            agentInstance = Agent.objects.get(id = agent)
        except:
            raise serializers.ValidationError(
                {'Erreur': [_("Vous devez selectionner un agent valide")]})

        vid = Video.objects.create(video = video, agent=agentInstance)
        return AGENT_IMAGES_URL + vid.video.url

class UploadAudioManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audio
        fields = ['id', 'audio', 'date_create']
        extra_kwargs = {
            'date_create': {'read_only': True, 'required': False},
            #'date_update': {'read_only': True, 'required': False},
        }
    def create(self, validated_data):
        audio = validated_data['audio']
        agent = self.context['agentid']
        try:
            agentInstance = Agent.objects.get(id = agent)
        except:
            raise serializers.ValidationError(
                {'Erreur': [_("Vous devez selectionner un agent valide")]})

        aud = Audio.objects.create(audio = audio, agent=agentInstance)
        return AGENT_IMAGES_URL + aud.audio.url


#####################   Entity   ########################
class Entity_SynonymeManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Synonyme
        fields = ['id', 'synonyme']
        # extra_kwargs = {
        #     'date_create': {'read_only': True, 'required': False},
        #     'date_update': {'read_only': True, 'required': False},
        # }
    def create(self, validated_data, value = None):
        for synonyme in validated_data:
            created_synonyme = Synonyme.objects.create(synonyme=synonyme['synonyme'], value=value)

    def update(self, validated_data, value = None):
        for synonyme in validated_data:
            if 'id' in synonyme:

                try:
                    created_synonyme = Synonyme.objects.get(id = synonyme['id'])
                except:
                    raise serializers.ValidationError(
                        {'Erreur': [_("L'un des synonymes de l'entité n'est pas reconnue")]})
                created_synonyme.synonyme = synonyme['synonyme']
                created_synonyme.save()
            else:
                tab = []
                tab.append(synonyme)
                Entity_SynonymeManagerSerializer.create(self,tab, value)



class Entity_ValueManagerSerializer(serializers.ModelSerializer):
    synonyme_set = Entity_SynonymeManagerSerializer(many=True, required=False)
    class Meta:
        model = Value
        fields = ['id', 'value','synonyme_set']
        # extra_kwargs = {
        #     'date_create': {'read_only': True, 'required': False},
        #     'date_update': {'read_only': True, 'required': False},
        # }


    def create(self, validated_data, entity=None):
        for value in validated_data:
            created_value = Value.objects.create(value = value['value'], entity = entity)
            Synonyme_set = value.pop('synonyme_set')
            Entity_SynonymeManagerSerializer.create(self, Synonyme_set, created_value)
    def update(self, validated_data, entity = None):
        for value in validated_data:
            if 'id' in value:

                try:
                    created_value = Value.objects.get(id = value['id'])
                except:
                    raise serializers.ValidationError(
                        {'Erreur': [_("L'un des valeurs de l'entité n'est pas reconnue")]})
                created_value.value = value['value']
                created_value.save()
                Synonyme_set = value.pop('synonyme_set')
                Entity_SynonymeManagerSerializer.update(self, Synonyme_set, created_value)
            else:
                tab = []
                tab.append(value)
                Entity_ValueManagerSerializer.create(self,tab, entity)



class EntityManagerSerializer(serializers.ModelSerializer):
    value_set = Entity_ValueManagerSerializer(many=True, required=False)
    class Meta:
        model = Entity
        fields = ['id', 'name', 'value_set']
        # extra_kwargs = {
        #     'date_create': {'read_only': True, 'required': False},
        #     'date_update': {'read_only': True, 'required': False},
        # }

    def verify_entity_name(self, str, agent_id, entity_id=-1):
        entity_name = str.upper()
        try:
            Entity.objects.exclude(id = entity_id).get(name=entity_name, agent = agent_id)
            return False
        except (Entity.DoesNotExist):
            return True

    def create(self, validated_data):
        try:
            agent = Agent.objects.get(id=self.context['agentid'])
        except:
            raise serializers.ValidationError(
                {'Erreur': [_("Agent non reconnue")]})
        Entity_Name = validated_data['name'].upper()
        # x = self.verify_entity_name(validated_data['name'], self.context['agentid'])
        x = EntityManagerSerializer.verify_entity_name(self, validated_data['name'], self.context['agentid'])
        if not x:
            raise serializers.ValidationError(
                {'Erreur': [_("Le nom de l'entité est deja existant, Vous devez choisir un autre!")]})
        entity = Entity.objects.create(name=Entity_Name, agent = agent)
        Entity_values = validated_data.pop('value_set')
        Entity_ValueManagerSerializer.create(self, Entity_values, entity)
        return entity

    def update(self, instance, validated_data):
        try:
            agent = Agent.objects.get(id=self.context['agentid'])
        except:
            raise serializers.ValidationError(
                {'Erreur': [_("Agent non reconnue")]})

        if 'id' in validated_data:
            try:
                Entity_obj  = Entity.objects.get(id = validated_data['id'])
            except:
                raise serializers.ValidationError(
                    {'Erreur': [_("Entity non reconnue")]})
            x = self.verify_entity_name(validated_data['name'], self.context['agentid'], Entity_obj.id)
            if x:
                Entity_obj.name = validated_data['name'].upper()
                Entity_obj.save()
            else:
                raise serializers.ValidationError(
                    {'Erreur': [_("Vous devez choisir un autre nom pour cette entité")]})
        if 'delete' in validated_data:
            to_deleted = validated_data.pop('delete')
            if 'values' in to_deleted:
                to_deleted_values = to_deleted.pop('values')
                for value in to_deleted_values:
                    try:
                        Value.objects.get(id = value).delete()
                    except:
                        raise serializers.ValidationError(
                            {'Erreur': [_("Vous devez verifier les valeurs des entités à supprimer")]})
            if 'synonymes' in to_deleted:
                to_deleted_synonymes = to_deleted.pop('synonymes')
                for synonyme in to_deleted_synonymes:
                    try:
                        Synonyme.objects.get(id=synonyme).delete()
                    except:
                        raise serializers.ValidationError(
                            {'Erreur': [_("Vous devez verifier les synonymes des entités à supprimer")]})


        Entity_values = validated_data.pop('value_set')
        Entity_ValueManagerSerializer.update(self, Entity_values, Entity_obj)

#####################   Entity   ########################

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'name', 'date_create', 'date_update', 'order']
        extra_kwargs = {'id': {'read_only': False, 'required': False}}

    def create(self, validated_data, intentID=None):

        try:
            intentObj=Intent.objects.get(id=intentID)
        except:
            raise serializers.ValidationError(
                {'Erreur': [_("Une erreur est parvenue lors de la recuperation de l'intention dans le bloc question_set")]})
        for question in validated_data:
            try:
                Question.objects.create(intent=intentObj, **question)
            except:
                Intent.objects.filter(id=intentID).delete()
                raise serializers.ValidationError({'Erreur': [_("erreur lors de l'insertion des questions")]})
        return True


class RandomTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = RandomText
        fields = ['id', 'name', 'date_create', 'date_update', 'order']
        extra_kwargs = {'id': {'read_only': False, 'required': False}}


class SimpleResponseSerializer(serializers.ModelSerializer):
    random_text_set = RandomTextSerializer(many=True, required=False)

    class Meta:
        model = SimpleResponse
        fields = ['id', 'date_create', 'date_update', 'random_text_set']
        extra_kwargs = {'id': {'read_only': False, 'required': False}}


class ButtonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Button
        fields = ['id', 'type', 'name', 'url', 'payload', 'phone_number', 'messenger_extensions', 'date_create', 'date_update', 'order']
        extra_kwargs = {'id': {'read_only': False, 'required': False},
                        'order':{'write_only': True, 'required': False},
                        'payload':{'required': False},
                        'url':{'required': False}}

    def create(self, validated_data, objectID=None, agentid=None, intentname=None, the_class=None):


        try:
            agent = Agent.objects.get(pk=int(agentid))
            if the_class == "IntentManagerSerializer":
                quickReply = QuickReply.objects.get(pk=int(objectID))
            elif the_class == "TextResponseSerializer":
                textResponse = TextResponse.objects.get(pk=int(objectID))
            elif the_class == "SliderSerializer":
                slider = Slider.objects.get(pk=int(objectID))
        except:
            if the_class == "IntentManagerSerializer":
                raise serializers.ValidationError(
                    {'Erreur': [_("Vous devez verifier la creation des boutons de quick reply")]})
            elif the_class == "TextResponseSerializer":
                raise serializers.ValidationError(
                    {'Erreur': [_("Vous devez verifier la creation des boutons de text response")]})
            elif the_class == "SliderSerializer":
                raise serializers.ValidationError(
                    {'Erreur': [_("Vous devez verifier la creation des boutons des Sliders")]})

        for button in validated_data:
            try:
                if not ('order' in button):
                    button['order']=0
                if not ('payload' in button):
                    pass
                    #button['payload'] = button['name']
                if the_class == "IntentManagerSerializer":
                    Button.objects.create(quick_reply=quickReply, **button)
                elif the_class == "TextResponseSerializer":
                    Button.objects.create(text_response=textResponse, **button)
                elif the_class == "SliderSerializer":
                    Button.objects.create(slider=slider, **button)

            except:
                if the_class == "IntentManagerSerializer":
                     raise serializers.ValidationError(
                        {'Erreur': [_("Vous devez verifier les bouttons quick reply")]})
                elif the_class == "TextResponseSerializer":
                    raise serializers.ValidationError(
                        {'Erreur': [_("Vous devez verifier les bouttons de text response")]})
                elif the_class == "SliderSerializer":
                    raise serializers.ValidationError(
                        {'Erreur': [_("Vous devez verifier les bouttons de slider")]})

    def update(self, instance, validated_data, objectID=None, agentid=None, intentname=None, the_class=None):


        try:

            agent = Agent.objects.get(pk=int(agentid))
            if the_class == "IntentManagerSerializer":
                quickReply = QuickReply.objects.get(pk=int(objectID))
            elif the_class == "TextResponseSerializer":
                textResponse = TextResponse.objects.get(pk=int(objectID))
            elif the_class == "SliderSerializer":
                slider = Slider.objects.get(pk=int(objectID))
        except:
            if the_class == "IntentManagerSerializer":
                raise serializers.ValidationError(
                    {'Erreur': [_("Vous devez verifier la creation des boutons de quick reply")]})
            elif the_class == "TextResponseSerializer":
                raise serializers.ValidationError(
                    {'Erreur': [_("Vous devez verifier la creation des boutons de text response")]})
            elif the_class == "SliderSerializer":
                raise serializers.ValidationError(
                    {'Erreur': [_("Vous devez verifier la creation des boutons des Sliders")]})

        for button in validated_data:
            if not 'id' in button:
                try:
                    if not ('order' in button):
                        button['order']=0
                    if not ('payload' in button):
                        button['payload'] = None

                    if the_class == "IntentManagerSerializer":
                        Button.objects.create(quick_reply=quickReply, **button)
                    elif the_class == "TextResponseSerializer":
                        Button.objects.create(text_response=textResponse, **button)
                    elif the_class == "SliderSerializer":
                        Button.objects.create(slider=slider, **button)

                except:
                    if the_class == "IntentManagerSerializer":
                         raise serializers.ValidationError(
                            {'Erreur': [_("Vous devez verifier les bouttons quick reply")]})
                    elif the_class == "TextResponseSerializer":
                        raise serializers.ValidationError(
                            {'Erreur': [_("Vous devez verifier les bouttons de text response")]})
                    elif the_class == "SliderSerializer":
                        raise serializers.ValidationError(
                            {'Erreur': [_("Vous devez verifier les bouttons de slider")]})
            elif 'id' in button and button['id']:
                try:
                    buttonInstance = Button.objects.get(id = button['id'])
                    buttonInstance.name = button['name']
                    if 'url' in button:
                        buttonInstance.url = button['url']
                    if 'payload' in button:
                        buttonInstance.payload = button['payload']
                    #buttonInstance.payload = button['payload']
                    buttonInstance.save()
                except:
                    if the_class == "IntentManagerSerializer":
                         raise serializers.ValidationError(
                            {'Erreur': [_("Vous devez verifier les bouttons quick reply")]})
                    elif the_class == "TextResponseSerializer":
                        raise serializers.ValidationError(
                            {'Erreur': [_("Vous devez verifier les bouttons de text response")]})
                    elif the_class == "SliderSerializer":
                        raise serializers.ValidationError(
                            {'Erreur': [_("Vous devez verifier les bouttons de slider")]})



""" Begin Persistent Menu """

class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class ButtonMenuSerializer(serializers.ModelSerializer):
    button_set = RecursiveField(many=True, required=False)

    class Meta:
        model = Button
        fields = ['id', 'name', 'url', 'payload', 'date_create', 'date_update', 'order', 'type', 'button_set']
        extra_kwargs = {'id': {'read_only': False, 'required': False},
                        'payload': {'read_only': True, 'required': False},
                        'url': {'read_only': True, 'required': False},
                        'date_create': {'read_only': True, 'required': False},
                        'date_update': {'read_only': True, 'required': False}
                        }
        depth = 1

    def delete_menu(self, agent):
        print("deleting menues of agent :", agent)
        menu_queryset = Menu.objects.filter(agent=agent)
        for m in menu_queryset:
            m.delete()
        # TODO : delete menu on the facebook page if connected to this agent

    def create(self, validated_data, objectID=None, agentID=None, the_class=None):

        try:
            agent=Agent.objects.get(pk=agentID)
        except(TypeError, ValueError, OverflowError, Agent.DoesNotExist):
            raise serializers.ValidationError({'Erreur': [_("Cet agent n'existe pas.")]})


        try:
            if the_class == "ButtonMenuSerializer":
                button_obj = Button.objects.get(pk=int(objectID))
            elif the_class == "MenuManagerSerializer":
                print(objectID)
                menu_obj = Menu.objects.get(pk=int(objectID))
        except:
            if the_class == "ButtonMenuSerializer":
                raise serializers.ValidationError(
                    {'Erreur': [_("Vous devez verifier la creation des boutons du menu.")]})

            if the_class == "MenuManagerSerializer":
                raise serializers.ValidationError(
                    {'Erreur': [_("Vous devez verifier la creation du menu.")]})

        for button in validated_data:
            button_set = None
            if 'button_set' in button:
                button_set = button.pop('button_set')
                print("button set", button_set)
                print(button)

            try:
                if the_class == "MenuManagerSerializer":
                    # print(**button)

                    button_menu = Button.objects.create(menu=menu_obj, **button)

                    if button_set:
                        ButtonMenuSerializer.create(self, button_set, button_menu.id, agentID, "ButtonMenuSerializer")

                elif the_class == "ButtonMenuSerializer":

                    button_submenu = Button.objects.create(sub_menu=button_obj, **button)

                    if button_set:
                        ButtonMenuSerializer.create(self, button_set, button_submenu.id, agentID, "ButtonMenuSerializer")
            except:
                ButtonMenuSerializer.delete_menu(self, agent)
                if the_class == "MenuManagerSerializer":
                    raise serializers.ValidationError(
                        {'Erreur': [_("Vous devez verifier la creation du menu.")]})

                elif the_class == "ButtonMenuSerializer":
                    raise serializers.ValidationError(
                        {'Erreur': [_("Vous devez verifier la creation des boutons du menu.")]})


    def update(self, instance, validated_data, agentID=None, the_class=None):

        try:
            agent=Agent.objects.get(pk=agentID)
        except(TypeError, ValueError, OverflowError, Agent.DoesNotExist):
            raise serializers.ValidationError({'Erreur': [_("Cet agent n'existe pas.")]})


        try:
            if the_class == "ButtonMenuSerializer":
                button_obj = Button.objects.get(pk=instance.id)
            elif the_class == "MenuManagerSerializer":
                menu_obj = Menu.objects.get(pk=instance.id)
        except:
            if the_class == "ButtonMenuSerializer":
                raise serializers.ValidationError(
                    {'Erreur': [_("Vous devez verifier la creation des boutons du menu.")]})

            if the_class == "MenuManagerSerializer":
                raise serializers.ValidationError(
                    {'Erreur': [_("Vous devez verifier la creation du menu.")]})

        for button in validated_data:
            button_set = None

            if 'button_set' in button:
                button_set = button.pop('button_set')

            if not 'id' in button:
                try:
                    if the_class == "MenuManagerSerializer":
                        buttonObjMenu = Button.objects.create(menu=menu_obj, **button)
                        if button_set:
                            ButtonMenuSerializer.update(self, buttonObjMenu, button_set, agentID, "ButtonMenuSerializer")
                    elif the_class == "ButtonMenuSerializer":
                        buttonObjSubMenu = Button.objects.create(sub_menu=button_obj, **button)
                        if button_set:
                            ButtonMenuSerializer.update(self, buttonObjSubMenu, button_set, agentID, "ButtonMenuSerializer")

                except:

                    ButtonMenuSerializer.delete_menu(self, agent)

                    if the_class == "MenuManagerSerializer":
                         raise serializers.ValidationError(
                            {'Erreur': [_("Vous devez verifier les bouttons principales du menu.")]})

                    elif the_class == "ButtonMenuSerializer":
                        raise serializers.ValidationError(
                            {'Erreur': [_("Vous devez verifier la creation des boutons du menu.")]})


            elif 'id' in button and button['id']:
                try:

                    buttonObj = Button.objects.get(id=button['id'])
                    buttonObj.name = button['name']
                    if 'url' in button:
                        buttonObj.url = button['url']
                    if 'payload' in button:
                        buttonObj.payload = button['payload']
                    if 'type' in button:
                        buttonObj.type = button['type']

                    buttonObj.save()

                    if button_set:
                        ButtonMenuSerializer.update(self, buttonObj, button_set, agentID, "ButtonMenuSerializer")

                except:
                    ButtonMenuSerializer.delete_menu(self, agent)

                    raise serializers.ValidationError({'Erreur': [_("Vous devez verifier le contenu des boutons principales du menu.")]})


class MenuManagerSerializer(serializers.ModelSerializer):
    button_set = ButtonMenuSerializer(many=True, required=False)

    class Meta:
        model = Menu
        fields = ['id', 'name', 'date_create', 'date_update', 'button_set']

        extra_kwargs = {
            'name': {'read_only': True, 'required': False},
            'date_create': {'read_only': True, 'required': False},
            'date_update': {'read_only': True, 'required': False}

        }

    def create(self, validated_data):

        agentID=self.context['agentid']
        print("agent id :", agentID)

        try:
            agent=Agent.objects.get(pk=agentID)
        except(TypeError, ValueError, OverflowError, Agent.DoesNotExist):
            raise serializers.ValidationError({'Erreur': [_("Cet agent n'existe pas")]})

        menu_queryset = Menu.objects.filter(agent=agent)
        if len(menu_queryset) > 0:
            raise serializers.ValidationError({'Erreur': [_("Il existe déja un menu pour cet agent!")]})


        if ((('button_set' in validated_data)) and (validated_data['button_set'])):
            button_set = validated_data.pop('button_set')
            print(button_set)
            menu_obj = Menu.objects.create(agent=agent)

            ButtonMenuSerializer.create(self, button_set, menu_obj.id, agentID, "MenuManagerSerializer")
        # else:
        #     raise serializers.ValidationError({'Erreur': [_("La création d'un menu persistent nécessite l'ajout d'au moins un bouton.")]})
        #
        # return "ok"

    def update(self, instance, validated_data):

        agentID=self.context['agentid']
        print("agent id :", agentID)

        try:
            agent=Agent.objects.get(pk=agentID)
        except(TypeError, ValueError, OverflowError, Agent.DoesNotExist):
            raise serializers.ValidationError({'Erreur': [_("Cet agent n'existe pas")]})


        if 'deleted' in validated_data and validated_data.get("deleted"):
            deleted = validated_data["deleted"]
            print("deleted :",  deleted)

            # get the principal buttons in the menu :
            button_query_set = Button.objects.filter(menu=instance)
            button_ids = [button.id for button in button_query_set]

            result = all(elem in deleted for elem in button_ids)

            for id in deleted:
                try:
                    button_obj = Button.objects.get(id=id)
                    button_obj.delete()
                except Button.DoesNotExist:
                    pass

            if result:
                if ((('button_set' in validated_data)) and (validated_data['button_set'])):
                    button_set = validated_data.pop('button_set')
                    ButtonMenuSerializer.update(self, instance, button_set, agentID, "MenuManagerSerializer")
                    return "ok"
                else:
                    # all principal buttons in the menu has been deleted, so we gonna delete the entire menu
                    instance.delete()
                    return "ok"

        if ((('button_set' in validated_data)) and (validated_data['button_set'])):
            button_set = validated_data.pop('button_set')

            ButtonMenuSerializer.update(self, instance, button_set, agentID, "MenuManagerSerializer")


""" End Persistent Menu """

class TextResponseSerializer(serializers.ModelSerializer):
    button_set = ButtonSerializer(many=True, required=False)

    class Meta:
        model = TextResponse
        fields = ['id', 'name', 'date_create', 'date_update', 'order', 'button_set']
        extra_kwargs = {'id': {'read_only': False, 'required': False}}

    def create(self, validated_data, mixedResponseid=None, agentid=None, intentname=None):
        """Handling the creating function of quick reply"""

        try:
            mixedResponse = MixedResponse.objects.get(pk=int(mixedResponseid))
            agent = Agent.objects.get(pk=int(agentid))
        except:
            Intent.objects.filter(name=intentname, agent=agent).delete()
            raise serializers.ValidationError(
                {'Erreur': [_("Vous devez verifier la creation de text response")]})
        for text_response in validated_data:
            print('#####', text_response)
            button_set = None
            if ((('button_set' in text_response)) or (text_response['button_set'])):
                button_set = text_response.pop('button_set')
            try:
                text_response = TextResponse.objects.create(mixed_response=mixedResponse, **text_response)
            except:
                Intent.objects.filter(name=intentname, agent=agent).delete()
                raise serializers.ValidationError(
                    {'Erreur': [_("Vous devez verifier le text response")]})
            if button_set:
                x = ButtonSerializer.create(self, button_set, text_response.id, agent.id,
                                                intentname, "TextResponseSerializer")
        return True

    def update(self, instance, validated_data, mixedResponseid=None, agentid=None, intentname=None):
        """Handling the creating function of quick reply"""

        try:
            mixedResponse = MixedResponse.objects.get(pk=int(mixedResponseid))
            agent = Agent.objects.get(pk=int(agentid))
        except:
            Intent.objects.filter(name=intentname, agent=agent).delete()
            raise serializers.ValidationError(
                {'Erreur': [_("Vous devez verifier la creation de text response")]})
        for text_response in validated_data:

            if not 'id' in text_response:
                button_set = None
                if ((('button_set' in text_response)) or (text_response['button_set'])):
                    button_set = text_response.pop('button_set')
                try:
                    text_response = TextResponse.objects.create(mixed_response=mixedResponse, **text_response)
                except:
                    raise serializers.ValidationError(
                        {'Erreur': [_("Vous devez verifier le text response")]})
                if button_set:
                    x = ButtonSerializer.create(self, button_set, text_response.id, agent.id,
                                                    intentname, "TextResponseSerializer")

            elif 'id' in text_response and text_response['id']:
                button_set = None
                if ((('button_set' in text_response)) or (text_response['button_set'])):
                    button_set = text_response.pop('button_set')
                try:
                    text_responseInstance = TextResponse.objects.get(id=text_response['id'])
                    text_responseInstance.name = text_response['name']
                    text_responseInstance.order = text_response['order']
                    text_responseInstance.save()

                except:
                    raise serializers.ValidationError(
                        {'Erreur': [_("Vous devez verifier le text response")]})
                if button_set:
                    x = ButtonSerializer.update(self, instance, button_set, text_responseInstance.id, agent.id,
                                                    intentname, "TextResponseSerializer")
        return True


class SliderSerializer(serializers.ModelSerializer):
    button_set = ButtonSerializer(many=True, required=False)

    class Meta:
        model = Slider
        fields = ['id', 'image', 'title', 'subtitle', 'url', 'date_create', 'date_update', 'order', 'button_set']
        extra_kwargs = {'id': {'read_only': False, 'required': False}}

    def create(self, validated_data, galleryid=None, agentid=None, intentname=None, path_to_user_folder=None):
        """Handling the creating function of gallery"""

        try:
            agent = Agent.objects.get(pk=int(agentid))
            galleryObj = Gallery.objects.get(pk=int(galleryid))
        except:
            Intent.objects.filter(name=intentname, agent=agent).delete()
            raise serializers.ValidationError(
                {'Erreur': [_("Vous devez verifier la creation de slider")]})
        for slider in validated_data:
            button_set = None
            if 'button_set' in slider:
                button_set = slider.pop('button_set')

            if "imagestr" in slider:
                try:
                    """convert the imagestr field to image field"""
                    format, imgstr = slider['imagestr'].split(';base64,')
                    ext = format.split('/')[-1]
                    imagefield = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
                    req = slider.copy()
                    del req['imagestr']
                    req['image'] = imagefield
                    sliderObj = Slider.objects.create(gallery=galleryObj, **req)
                except:
                    Intent.objects.filter(name=intentname, agent=agent).delete()
                    raise serializers.ValidationError(
                        {'Erreur': [_("Vous devez verifier le contenu des objets slider")]})

            elif "imageName" in slider:
                try:
                    image_path = os.path.join(path_to_user_folder, 'images', str(slider["imageName"]))
                    del slider["imageName"]
                    try:
                        slider['image'] = File(open(image_path, 'rb'))
                    except:
                        pass
                    sliderObj = Slider.objects.create(gallery=galleryObj, **slider)
                except:
                    Intent.objects.filter(name=intentname, agent=agent).delete()
                    raise serializers.ValidationError(
                        {'Erreur': [_(
                            "Vous devez verifier le contenue des images dans l'objet slider lors de l'import/traduction de l'intent.")]})
            else:
                try:
                    sliderObj = Slider.objects.create(gallery=galleryObj, **slider)
                except:
                    Intent.objects.filter(name=intentname, agent=agent).delete()
                    raise serializers.ValidationError(
                        {'Erreur': [_("Vous devez verifier le contenu des objets slider")]})


            if button_set:
                x = ButtonSerializer.create(self, button_set, sliderObj.id, agent.id,
                                                intentname, "SliderSerializer")
        return True

    def update(self, instance, validated_data, galleryid=None, agentid=None, intentname=None):
        """Handling the creating function of gallery"""

        try:
            agent = Agent.objects.get(pk=int(agentid))
            galleryObj = Gallery.objects.get(pk=int(galleryid))
        except:
            Intent.objects.filter(name=intentname, agent=agent).delete()
            raise serializers.ValidationError(
                {'Erreur': [_("Vous devez verifier la creation de slider")]})
        for slider in validated_data:
            if not 'id' in slider:
                button_set = None
                if ((('button_set' in slider)) or (slider['button_set'])):
                    button_set = slider.pop('button_set')
                try:
                    """convert the imagestr field to image field"""
                    format, imgstr = slider['imagestr'].split(';base64,')
                    ext = format.split('/')[-1]
                    imagefield = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
                    req = slider.copy()
                    del req['imagestr']
                    req['image'] = imagefield
                    sliderObj = Slider.objects.create(gallery=galleryObj, **req)
                except:
                    raise serializers.ValidationError(
                        {'Erreur': [_("Vous devez verifier le contenu des objets slider")]})
                if button_set:
                    x = ButtonSerializer.update(self, instance, button_set, sliderObj.id, agent.id,
                                                    intentname, "SliderSerializer")
            elif 'id' in slider and slider['id']:
                button_set = None
                if ((('button_set' in slider)) or (slider['button_set'])):
                    button_set = slider.pop('button_set')


                if 'imagestr' in slider and slider['imagestr']:
                    try:
                        """convert the imagestr field to image field"""
                        format, imgstr = slider['imagestr'].split(';base64,')
                        ext = format.split('/')[-1]
                        imagefield = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

                        field = Slider.objects.get(id=slider['id'])
                        field.image = imagefield
                        field.order = slider['order']
                        field.title = slider['title']
                        field.subtitle = slider['subtitle']
                        field.url = slider['url']
                        field.save()

                    except:
                        raise serializers.ValidationError({'Erreur': [_("Vous devez verifier le contenue des images slider")]})
                    if button_set:
                        x = ButtonSerializer.update(self, instance, button_set, field.id, agent.id,
                                                    intentname, "SliderSerializer")

                elif 'imageurl' in slider and slider['imageurl']:
                    try:
                        req = Slider.objects.get(id=slider['id'])
                        req.order = slider['order']
                        req.title = slider['title']
                        req.subtitle = slider['subtitle']
                        req.url = slider['url']
                        req.save()
                    except:
                        raise serializers.ValidationError(
                            {'Erreur': [_("Vous devez verifier le contenue des images slider ")]})
                    if button_set:
                        x = ButtonSerializer.update(self, instance, button_set, req.id, agent.id,
                                                    intentname, "SliderSerializer")




        return True


class GallerySerializer(serializers.ModelSerializer):
    slider_set = SliderSerializer(many=True)

    class Meta:
        model = Gallery
        fields = ['id', 'date_create', 'date_update', 'order', 'slider_set']
        extra_kwargs = {'id': {'read_only': False, 'required': False}}

    def create(self, validated_data, mixedResponseid=None, agentid=None, intentname=None, path_to_user_folder=None):
        """Handling the creating function of gallery"""


        try:
            agent = Agent.objects.get(pk=int(agentid))
            mixedResponse = MixedResponse.objects.get(pk=int(mixedResponseid))
        except:
            Intent.objects.filter(name=intentname, agent=agent).delete()
            raise serializers.ValidationError(
                {'Erreur': [_("Vous devez verifier la creation de gallery")]})
        for gallery in validated_data:
            slider_set = None
            if ((('slider_set' in gallery)) or (gallery['slider_set'])):
                slider_set = gallery.pop('slider_set')
            try:
                galleryObj = Gallery.objects.create(mixed_response=mixedResponse, **gallery)
            except:
                Intent.objects.filter(name=intentname, agent=agent).delete()
                raise serializers.ValidationError(
                    {'Erreur': [_("Vous devez verifier le gallery")]})
            if slider_set:
                if path_to_user_folder is None:
                    SliderSerializer.create(self, slider_set, galleryObj.id, agent.id,
                                                    intentname)
                else:
                    SliderSerializer.create(self, slider_set, galleryObj.id, agent.id,
                                            intentname, path_to_user_folder)
        return True

    def update(self, instance, validated_data, mixedResponseid=None, agentid=None, intentname=None):
        """Handling the creating function of gallery"""

        try:
            agent = Agent.objects.get(pk=int(agentid))
            mixedResponse = MixedResponse.objects.get(pk=int(mixedResponseid))
        except:
            Intent.objects.filter(name=intentname, agent=agent).delete()
            raise serializers.ValidationError(
                {'Erreur': [_("Vous devez verifier la creation de gallery")]})
        for gallery in validated_data:
            if not 'id' in gallery:
                slider_set = None
                if ((('slider_set' in gallery)) or (gallery['slider_set'])):
                    slider_set = gallery.pop('slider_set')
                try:
                    galleryObj = Gallery.objects.create(mixed_response=mixedResponse, **gallery)
                except:
                    Intent.objects.filter(name=intentname, agent=agent).delete()
                    raise serializers.ValidationError(
                        {'Erreur': [_("Vous devez verifier le gallery")]})
                if slider_set:
                    x = SliderSerializer.create(self, slider_set, galleryObj.id, agent.id,
                                                    intentname)

            elif 'id' in gallery and gallery['id']:
                slider_set = None
                if ((('slider_set' in gallery)) or (gallery['slider_set'])):
                    slider_set = gallery.pop('slider_set')

                galleryInstance = Gallery.objects.get(id=gallery['id'])
                galleryInstance.order = gallery['order']
                galleryInstance.save()

                if slider_set:
                    x = SliderSerializer.update(self, instance, slider_set, galleryInstance.id, agent.id,
                                                    intentname)

        return True




class QuickReplySerializer(serializers.ModelSerializer):
    button_set = ButtonSerializer(many=True)

    class Meta:
        model = QuickReply
        fields = ['id', 'name', 'date_create', 'date_update', 'order', 'button_set']
        extra_kwargs = {'id': {'read_only': False, 'required': False}}

    def create(self, validated_data, mixedResponseid=None, agentid=None, intentname=None):
        """Handling the creating function of quick reply"""

        try:
            agent = Agent.objects.get(pk=int(agentid))
            mixedResponse = MixedResponse.objects.get(pk=int(mixedResponseid))
        except:
            Intent.objects.filter(name=intentname, agent=agent).delete()
            raise serializers.ValidationError(
                {'Erreur': [_("Vous devez verifier la creation de quick reply")]})
        for quick_reply in validated_data:
            button_set = None
            if ((('button_set' in quick_reply)) or (quick_reply['button_set'])):
                button_set = quick_reply.pop('button_set')
            try:
                quickReply = QuickReply.objects.create(mixed_response=mixedResponse, **quick_reply)
            except:
                Intent.objects.filter(name=intentname, agent=agent).delete()
                raise serializers.ValidationError(
                    {'Erreur': [_("Vous devez verifier le quick reply")]})
            if button_set:
                x = ButtonSerializer.create(self, button_set, quickReply.id, agent.id,
                                                intentname, "IntentManagerSerializer")
        return True

    def update(self, instance, validated_data, mixedResponseid=None, agentid=None, intentname=None):
        """Handling the updating function of quick reply"""

        try:
            agent = Agent.objects.get(pk=int(agentid))
            mixedResponse = MixedResponse.objects.get(pk=int(mixedResponseid))
        except:
            Intent.objects.filter(name=intentname, agent=agent).delete()
            raise serializers.ValidationError(
                {'Erreur': [_("Vous devez verifier la creation de quick reply")]})
        for quick_reply in validated_data:
            if not 'id' in quick_reply:
                button_set = None
                if ((('button_set' in quick_reply)) or (quick_reply['button_set'])):
                    button_set = quick_reply.pop('button_set')
                try:
                    quickReply = QuickReply.objects.create(mixed_response=mixedResponse, **quick_reply)
                except:
                    Intent.objects.filter(name=intentname, agent=agent).delete()
                    raise serializers.ValidationError(
                        {'Erreur': [_("Vous devez verifier le quick reply")]})
                if button_set:
                    x = ButtonSerializer.create(self, button_set, quickReply.id, agent.id,
                                                    intentname, "IntentManagerSerializer")
            elif 'id' in quick_reply and quick_reply['id']:
                button_set = None
                if ((('button_set' in quick_reply)) or (quick_reply['button_set'])):
                    button_set = quick_reply.pop('button_set')

                quick_replyInstance = QuickReply.objects.get(id=quick_reply['id'])
                quick_replyInstance.name = quick_reply['name']
                quick_replyInstance.order = quick_reply['order']
                quick_replyInstance.save()

                if button_set:
                    x = ButtonSerializer.update(self, instance, button_set, quick_replyInstance.id, agent.id,
                                                intentname, "IntentManagerSerializer")
        return True



class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ['id', 'date_create', 'date_update', 'order', 'image']
        extra_kwargs = {'id': {'read_only': False, 'required': False}}


class MixedResponseSerializer(serializers.ModelSerializer):
    text_response_set = TextResponseSerializer(many=True, required=False)
    gallery_set = GallerySerializer(many=True, required=False)
    quick_reply_set = QuickReplySerializer(many=True, required=False)
    image_set = ImageSerializer(many=True, required=False)

    class Meta:
        model = MixedResponse
        fields = ['id', 'date_create', 'date_update', 'text_response_set', 'gallery_set', 'quick_reply_set',
                  'image_set']
        extra_kwargs = {'id': {'read_only': False, 'required': False}}


class BlockResponseSerializer(serializers.ModelSerializer):
    simple_response_set = SimpleResponseSerializer(many=True, required=False)
    mixed_response_set = MixedResponseSerializer(many=True, required=False)

    class Meta:
        model = BlockResponse
        fields = ['id', 'is_complex', 'category', 'date_create', 'date_update', 'simple_response_set', 'mixed_response_set']
        extra_kwargs = {'id': {'read_only': False, 'required': False}}


class OutputContextSerializer(serializers.ModelSerializer):

    class Meta:
        model = OutputContext
        fields = ['id', 'date_create', 'date_update', 'outContext']
        extra_kwargs = {'id': {'read_only': False, 'required': False}}

    def create(self, validated_data, agentID=None, intentID=None):

        try:
            agent=Agent.objects.get(id=agentID)
            intentObj=Intent.objects.get(id=intentID)
        except:
            raise serializers.ValidationError(
                {"erreur": "Erreur lors de l'importation de l'agent/intent dans le bloc output context"})
        intent_ids = [intent.id for intent in Intent.objects.filter(agent=agent)]
        for output_context in validated_data:

            output_context_obj = OutputContext.objects.filter(outContext=output_context["outContext"],
                                                              intent__in=intent_ids)
            if len(output_context_obj) > 0:
                Intent.objects.filter(id=intentID).delete()
                raise serializers.ValidationError(
                    {"erreur": "Cet output context est deja existant, veuillez utlizer un autre"})

            try:
                out_context_obj = OutputContext.objects.create(**output_context, intent=intentObj)
            except:
                Intent.objects.filter(id=intentID).delete()
                raise serializers.ValidationError({'Erreur': [_("erreur lors de l'insertion des output context")]})
        return True


class InputContextSerializer(serializers.ModelSerializer):
    output_context_name = serializers.CharField(source='outContext.outContext', required=False)
    class Meta:
        model = InputContext
        fields = ['id', 'date_create', 'date_update', "outContext", "output_context_name", "intent"]
        extra_kwargs = {
                        'outContext': {'read_only': True, 'required': False},
                        'output_context_name': {'read_only': True, 'required': False},
                        'intent': { 'required': False}}

    def create(self, validated_data, agentID=None, intentID=None):
        print('Hello 1')

        try:
            print('Hello 1')
            agent=Agent.objects.get(id=agentID)
            intentObj=Intent.objects.get(id=intentID)
            intentList = Intent.objects.filter(agent = agent)
            print('Hello 1')
        except:
            raise serializers.ValidationError(
                {"erreur": "Erreur lors de l'importation de l'agent/intent dans le bloc output context"})

        for input_context in validated_data:
            if 'Outname' in input_context and input_context["Outname"]:
                print('Hello 1')
                existOutputContext = OutputContext.objects.filter(outContext=input_context["Outname"], intent__in = intentList)
            else:
                existOutputContext = OutputContext.objects.filter(id=input_context["outContextID"], intent__in = intentList)

            if len(existOutputContext) > 0:
                try:
                    print('Hello 1')
                    if 'Outname' in input_context and input_context["Outname"]:
                        relatedOutContext = OutputContext.objects.get(outContext=input_context["Outname"], intent__in = intentList)
                        print('Hello 1')
                        input_context_obj = InputContext.objects.create(intent=intentObj,
                                                                        outContext=relatedOutContext)
                    else:
                        relatedOutContext = OutputContext.objects.get(id=input_context["outContextID"])
                        input_context_obj = InputContext.objects.create(intent=intentObj,
                                                                    outContext=relatedOutContext)
                except:
                    Intent.objects.filter(id=intentID).delete()
                    raise serializers.ValidationError(
                        {'Erreur': [_("erreur lors de l'insertion des input context")]})
            else:
                Intent.objects.filter(id=intentID).delete()
                raise serializers.ValidationError(
                    {'Erreur': [_(
                        "Vous devez inserer un input context referencier pour un output context deja existant et appartient au meme agent")]})

class AddDefaultIntentManagerSerializer(serializers.Serializer):
    defaultIntentID = serializers.ListField(child=serializers.IntegerField())

    def create(self, validated_data):
        req = self.context['request']
        agentID = self.context['agentid']
        intentList = []
        for intentID in validated_data['defaultIntentID']:
            intent = Intent.objects.get(id = intentID)
            if intent.agent.is_default:
                intentList.append(intentID)
            else:
                pass

        queryset = Intent.objects.filter(id__in=intentList)
        intentsdata = export_serializers.IntentManagerSerializer(queryset, many=True)
        print("data", intentsdata.data)
        for intentData in intentsdata.data:
            serializer2 = IntentManagerSerializer.create(self,intentData)
        return validated_data['defaultIntentID']


class FilteredListSerializerEntity(serializers.ListSerializer):
    """Filter the list of object in nested serializer according to the connected user_profile"""

    def to_representation(self, data):
        data = data.all()
        return super(FilteredListSerializerEntity, self).to_representation(data)



class IntentEntityManagerSerializer(serializers.ModelSerializer):
    entity = EntityManagerSerializer(many=False, required = True)
    class Meta:
        model = Entity_Intent
        fields = ['id',  'entity', 'prompt_response', 'is_required']
    extra_kwargs = {
            'entity': {'read_only': True, 'required': False},
        }

    def create(self, validated_data, intent=None):
        #validated_data.reverse()
        print('####entity_list####: ', validated_data)
        for entity in validated_data:
            try:
                EntityObj = Entity.objects.get(id = entity['entity'])
            except:
                raise serializers.ValidationError({'Erreur': [_("vous devez choisir une entitée valide")]})

            exist_relations = Entity_Intent.objects.filter(intent=intent).values_list('entity', flat = True)
            if not EntityObj.id in exist_relations:
                if 'prompt_response' in entity:
                    Entity_Intent.objects.create(prompt_response = entity['prompt_response'],
                                          is_required = entity['is_required'], entity = EntityObj, intent = intent)
                else:
                    Entity_Intent.objects.create(is_required=False, entity=EntityObj, intent=intent)
            else:
                pass
    def update(self, validated_data, intent= None):
        #validated_data.reverse()
        print('####entity_list####: ', validated_data)
        for entity in validated_data:
            if 'id' in entity:
                try:
                    Relation = Entity_Intent.objects.get(id=entity['id'])
                except:
                    raise serializers.ValidationError({'Erreur': [_("vous devez verfier les entitées liées a cette intent")]})
                Relation.prompt_response = entity['prompt_response']
                Relation.is_required = entity['is_required']
                Relation.save()

            else:
                listEntity = []
                listEntity.append(entity)
                IntentEntityManagerSerializer.create(self,listEntity,intent)

############# AUDIO/VIDEO ####################
class IntentVideoManagerSerializer(serializers.ModelSerializer):
    video = UploadVideoManagerSerializer(many=False, required = True)
    class Meta:
        model = Video_Intent
        fields = ['id', 'video']
    extra_kwargs = {
            'video': {'read_only': True, 'required': False},
        }
    def create(self, validated_data, intent=None):

        for video in validated_data:

            try:
                video_obj = Video.objects.get(video__contains=video['url'], agent = self.context['agentid'])
            except:
                Intent.objects.filter(id=intent.id).delete()
                raise serializers.ValidationError({'Erreur': [_("vous devez choisir une video valide")]})
            print('11')
            Video_Intent.objects.create(video=video_obj, intent=intent)

    def update(self, validated_data, intent= None):
        for video in validated_data:
            if 'id' in video:
                pass

            else:
                listvideo = []
                listvideo.append(video)
                IntentVideoManagerSerializer.create(self,listvideo,intent)




class IntentAudioManagerSerializer(serializers.ModelSerializer):
    audio = UploadAudioManagerSerializer(many=False, required = True)
    class Meta:
        model = Audio_Intent
        fields = ['id', 'audio']
    extra_kwargs = {
            'audio': {'read_only': True, 'required': False},
        }
    def create(self, validated_data, intent=None):

        for audio in validated_data:

            try:
                audio_obj = Audio.objects.get(audio__contains=audio['url'], agent = self.context['agentid'])
            except:
                Intent.objects.filter(id=intent.id).delete()
                raise serializers.ValidationError({'Erreur': [_("vous devez choisir une audio valide")]})
            Audio_Intent.objects.create(audio=audio_obj, intent=intent)

    def update(self, validated_data, intent= None):
        for audio in validated_data:
            if 'id' in audio:
                pass

            else:
                listaudio = []
                listaudio.append(audio)
                IntentAudioManagerSerializer.create(self,listaudio,intent)


class DependingNavigationManagerSerializer(serializers.ModelSerializer):
    intent = serializers.SerializerMethodField()
    class Meta:
        model = DependingNavigation
        fields = ['id', 'intent']
        extra_kwargs = {
            'id': {'read_only': True, 'required': False},
            #'date_update': {'read_only': True, 'required': False},
        }
    def get_intent(self, obj):
        return (obj.intent.name)
    def create(self, validated_data, nav_intent=None):

        for depend in validated_data:
            try:
                intentObj = Intent.objects.get(id=depend)
            except:
                raise serializers.ValidationError(
                    {'Erreur': [_("Vous devez choisir une intention de dependance valide")]})
            DependingNavigation.objects.create(intent = intentObj, nav_intent=nav_intent)


class NavigationIntentManagerSerialiser(serializers.ModelSerializer):
    related_depending = DependingNavigationManagerSerializer(many=True, required = True)
    redirection = serializers.SerializerMethodField()
    #echec = serializers.SerializerMethodField()
    class Meta:
        model = NavigationIntent
        fields = ['id', 'nb_tentative', 'redirection', 'echec', 'related_depending']
    extra_kwargs = {
            'id': {'read_only': True, 'required': False},
        }
    def get_redirection(self, obj):
        return (obj.redirection.name)
    # def get_echec(self, obj):
    #     return (obj.echec.name)
    def create(self, validated_data, intent=None):

        for navigation in validated_data:

            try:
                #redirection_intent = Intent.objects.get(id=navigation['redirection'], agent = intent.agent.id)
                echec_intent = Intent.objects.get(id=navigation['echec'], agent = intent.agent.id)
            except:
                #Intent.objects.filter(id=intent.id).delete()
                raise serializers.ValidationError({'Erreur': [_("vous devez choisir une intention d'echec valide")]})

            nav_intent= NavigationIntent.objects.create(nb_tentative=navigation['nb_tentative'], redirection=intent, echec=echec_intent, intent=intent)

            if 'related_depending' in navigation:
                depending_creation = DependingNavigationManagerSerializer.create(self, navigation['related_depending'], nav_intent)
            else:
                pass

    def update(self, validated_data, intent= None):
        for navigation in validated_data:
            if 'id' in navigation:
                try:
                    navigation_intent = NavigationIntent.objects.get(id=navigation['id'])
                    echec_intent = Intent.objects.get(id=navigation['echec'], agent=intent.agent.id)
                except:
                    #Intent.objects.filter(id=intent.id).delete()
                    raise serializers.ValidationError(
                        {'Erreur': [_("vous devez choisir une intention d'echec valide")]})
                navigation_intent.echec = echec_intent
                navigation_intent.nb_tentative = navigation['nb_tentative']
                navigation_intent.save()
                related_depending = navigation['related_depending']

                for dependance in related_depending:
                    if 'id' in dependance:
                        pass

                    else:
                        "it is a new dependance. Create it"
                        try:
                            intentObj = Intent.objects.get(id=dependance['intent'])
                        except:
                            raise serializers.ValidationError(
                                {'Erreur': [_("Vous devez choisir une intention de dependance valide")]})
                        DependingNavigation.objects.create(intent=intentObj, nav_intent=navigation_intent)


            else:
                exist_navigation_intent = NavigationIntent.objects.filter(intent=intent)
                if len(exist_navigation_intent)>0:
                    raise serializers.ValidationError(
                        {'Erreur': [_("Vous devez specifier un seul bloc de navigation par intent")]})
                nav=[]
                nav.append(navigation)
                navigations = NavigationIntentManagerSerialiser.create(self, nav, intent)

                pass



class IntentManagerSerializer(serializers.ModelSerializer):
    question_set = QuestionSerializer(many=True, required=False)
    block_response_set = BlockResponseSerializer(many=True, required=False)
    output_context_set = OutputContextSerializer(many=True, required=False)
    input_context_set = InputContextSerializer(many=True, required=False)
    #related_entity = IntentEntityManagerSerializer(many=True, required=False)
    related_entity =serializers.SerializerMethodField()
    related_navigation = NavigationIntentManagerSerialiser(many=True, required=False)
    related_videos = IntentVideoManagerSerializer(many=True, required=False)
    related_audios = IntentAudioManagerSerializer(many=True, required=False)
    class Meta:
        model = Intent
        fields = ['id', 'name', 'agent', 'date_create', 'date_update', 'description', 'is_depart', 'fulfillment', 'is_none_response', 'question_set','block_response_set', 'related_videos', 'related_audios', 'output_context_set', 'input_context_set', 'related_entity', 'related_navigation']
        extra_kwargs = {
            'date_create': {'read_only': True, 'required': False},
            'date_update': {'read_only': True, 'required': False},
            'agent': {'read_only': True, 'required': True},
            'is_depart': {'read_only': True},
            'is_none_response': {'read_only': True},
            'description': {'required': False},

        }

    def get_related_entity(self, instance):
        related_entity = instance.related_entity.all().order_by('id')
        return IntentEntityManagerSerializer(related_entity, many=True).data


    def create(self, validated_data):

        if "path_to_user_folder" in self.context:
            path_to_user_folder = self.context["path_to_user_folder"]
        else:
            path_to_user_folder = None

        agentID=self.context['agentid']
        if 'request' in self.context and self.context['request']:
            request=self.context['request']
        else:
            request = "None"

        try:
            agent=Agent.objects.get(pk=agentID)
        except(TypeError, ValueError, OverflowError, Agent.DoesNotExist):
            raise serializers.ValidationError({'Erreur': [_("Cet agent n'existe pas")]})

        try:
            intentName=validated_data['name']
        except:
            raise serializers.ValidationError({'Erreur': [_("vous devez specifier le nom de l'intent à créer")]})

        try:
            des=validated_data['description']
        except:
            des = "pas de description pour cette intent"


        if len(Intent.objects.filter(name=intentName, agent=agent))>0:
            raise serializers.ValidationError({'Erreur': [_("Le nom de l'intent à créer est deja existant, vous devez choisir un autre")]})
        if 'fulfillment' in validated_data:
            Intent.objects.create(name=validated_data['name'], description = validated_data['description'], agent=agent, fulfillment = validated_data['fulfillment'])
        else:
            Intent.objects.create(name=validated_data['name'], description = validated_data['description'], agent=agent)

        try:
            intentObj=Intent.objects.get(name=intentName, agent=agent)

            if "/agents_import" in request.path:
                is_active = validated_data['is_active']
                is_none_response = validated_data['is_none_response']
                is_depart = validated_data['is_depart']
                intentObj.is_active = is_active
                intentObj.is_none_response = is_none_response
                intentObj.is_depart = is_depart
                intentObj.save()
                print('#####Hello')

            if "/intents_import" in request.path:
                is_active = validated_data['is_active']
                is_none_response = validated_data['is_none_response']
                is_depart = validated_data['is_depart']
                intentObj.is_active = is_active
                intentObj.is_none_response = is_none_response
                intentObj.is_depart = is_depart
                intentObj.save()
                print('#####Hello import intent')

        except(TypeError, ValueError, OverflowError, Intent.DoesNotExist):
            raise serializers.ValidationError({'Erreur': [_("Intent n'a pas été créer pour des raisons inconnues")]})

        """Handling the question set"""
        if 'question_set' in validated_data and validated_data['question_set']:
            question_set = validated_data.pop('question_set')
            questionPostResult = QuestionSerializer.create(self, question_set, intentObj.id)

        """Handling the Output Context"""
        if 'output_context_set' in validated_data or validated_data.get("output_context_set"):
            if not "/agents_import" in request.path or not "/intents_import" in request.path:
                output_context_set = validated_data.pop('output_context_set')
                outputContextPostResult=OutputContextSerializer.create(self, output_context_set, agent.id, intentObj.id)
            else:
                pass

        """Handling the input Context"""
        if 'input_context_set' in validated_data or validated_data.get("input_context_set"):
            #here
            if not "/agents_import" in request.path and not "/intents_import" in request.path:
                input_context_set = validated_data.pop('input_context_set')
                inputContextPostResult=InputContextSerializer.create(self, input_context_set, agent.id, intentObj.id)
            else:
                pass

        """Handling the entity relations"""
        if 'related_entity_list' in validated_data or validated_data.get("related_entity_list"):
            related_entity = validated_data.pop('related_entity_list')
            entity=IntentEntityManagerSerializer.create(self, related_entity, intentObj)

        """Handling the navigation relations"""
        if ('related_navigation_list' in validated_data or validated_data.get("related_navigation_list"))\
                and not('related_entity_list' in validated_data or validated_data.get("related_entity_list")):
            related_navigation = validated_data.pop('related_navigation_list')
            navigation=NavigationIntentManagerSerialiser.create(self, related_navigation, intentObj)

        """Handling the video relations"""
        if 'related_video_list' in validated_data or validated_data.get("related_video_list"):
            related_videos = validated_data.pop('related_video_list')
            video=IntentVideoManagerSerializer.create(self, related_videos, intentObj)

        """Handling the audio relations"""
        if 'related_audio_list' in validated_data or validated_data.get("related_audio_list"):
            related_audios = validated_data.pop('related_audio_list')
            audio=IntentAudioManagerSerializer.create(self, related_audios, intentObj)

        """ Handling audios / intent translation"""
        if 'related_audioExportTranslate' in validated_data or validated_data.get('related_audioExportTranslate'):
            for audio in validated_data["related_audioExportTranslate"]:
                try:
                    audio_path = os.path.join(path_to_user_folder, 'audios', str(audio["audio"]))
                    audio['audio'] = File(open(audio_path, 'rb'))
                    audioObj = Audio.objects.create(audio=audio["audio"], agent=agent)
                    Audio_Intent.objects.create(audio=audioObj, intent=intentObj)
                except Exception as e:
                    Intent.objects.filter(name=validated_data['name'], agent=agent).delete()
                    raise serializers.ValidationError(
                        {'Erreur': [_("Vous devez verifier le contenue des audios.")]})

        """ Handling videos / intent translation"""
        if 'related_videoExportTranslate' in validated_data or validated_data.get('related_videoExportTranslate'):
            for video in validated_data["related_videoExportTranslate"]:
                try:
                    video_path = os.path.join(path_to_user_folder, 'videos', str(video["video"]))
                    video['video'] = File(open(video_path, 'rb'))
                    videoObj = Video.objects.create(video=video["video"], agent=agent)
                    Video_Intent.objects.create(video=videoObj, intent=intentObj)
                except Exception as e:
                    Intent.objects.filter(name=validated_data['name'], agent=agent).delete()
                    raise serializers.ValidationError(
                        {'Erreur': [_("Vous devez verifier le contenue des videos.")]})

        """ Handling entities / intent translation"""
        if 'related_entityExportTranslate' in validated_data or validated_data.get('related_entityExportTranslate'):
            entities = validated_data.pop('related_entityExportTranslate')
            entity_list = []
            for entity in entities:
                if entity["entity"]["is_default"]:
                    try:
                        entityObj = Entity.objects.get(name=entity["entity"]["name"], agent=agent)
                    except (Entity.DoesNotExist):
                        raise serializers.ValidationError({'Erreur': [_("Entité système non trouvé.")]})
                else:
                    try:
                        entityObj = Entity.objects.get(name=str(entity["entity"]["name"]).upper(), agent=agent)
                    except (Entity.DoesNotExist):
                        entityObj = EntityManagerSerializer.create(self, entity["entity"])
                entityIntent = dict()
                entityIntent["entity"] = entityObj.id
                entityIntent["prompt_response"] = entity["prompt_response"]
                entityIntent["is_required"] = entity["is_required"]
                entity_list.append(entityIntent)
            x = IntentEntityManagerSerializer.create(self, entity_list, intentObj)





        """Handling the bloc response set"""
        #if not validated_data['block_response_set']:
        #    if not 'fulfillment' in validated_data:
        #        intentObj.delete()
        #        raise serializers.ValidationError({'Erreur': [_("Vous devez specifier une reponse")]})
        #    elif not validated_data['fulfillment']:
        #        intentObj.delete()
        #        raise serializers.ValidationError({'Erreur': [_("Vous devez specifier une reponse")]})

        # elif 'block_response_set' in validated_data:
        #     if not validated_data['block_response_set'] and not validated_data['fulfillment']:
        #         intentObj.delete()
        #         raise serializers.ValidationError({'Erreur': [_("Vous devez specifier une reponse")]})


        if 'block_response_set' in validated_data and validated_data['block_response_set']:
            block_response = validated_data.pop('block_response_set')
            for block_response_set in block_response:
                if ('simple_response_set' in block_response_set and block_response_set['simple_response_set']) and ('mixed_response_set' in block_response_set and block_response_set['mixed_response_set']):
                    raise serializers.ValidationError({'Erreur': [_("Vous devez specifier un seul type de reponse")]})

                """Handling the simple response"""
                if ('simple_response_set' in block_response_set and block_response_set['simple_response_set']):
                    if 'is_complex' in block_response_set and block_response_set['is_complex']:
                        Intent.objects.filter(name=validated_data['name'], agent=agent).delete()
                        raise serializers.ValidationError({'Erreur': [_("Vous devez verifier le type de reponse")]})
                    simple_response_set = block_response_set.pop('simple_response_set')[0]

                    if "mixed_response_set" in block_response_set:
                        del block_response_set["mixed_response_set"]

                    try:
                        blockResponse=BlockResponse.objects.create(intent=intentObj,**block_response_set)

                    except:
                        Intent.objects.filter(name=validated_data['name'], agent=agent).delete()
                        raise serializers.ValidationError({'Erreur': [_("Vous devez specifier le type de reponse")]})

                    """Handling the random text set"""
                    if (not ('random_text_set' in simple_response_set)) or (not simple_response_set['random_text_set']):
                        Intent.objects.filter(name=validated_data['name'], agent=agent).delete()
                        raise serializers.ValidationError({'Erreur': [_("Vous devez inserer des reponses valides")]})
                    simpleResponse=SimpleResponse.objects.create(block_response=blockResponse)

                    """Handling the random text of simple response"""
                    random_text_set=simple_response_set.pop('random_text_set')
                    for text in random_text_set:
                        try:
                            RandomText.objects.create(simple_response=simpleResponse,**text)
                        except:
                            Intent.objects.filter(name=validated_data['name'], agent=agent).delete()
                            raise serializers.ValidationError({'Erreur': [_("Vous devez verifier le contenue de random_text_reponse")]})

                """Handling the mixed response"""
                if ('mixed_response_set' in block_response_set and block_response_set['mixed_response_set']):
                    if 'is_complex' in block_response_set and not block_response_set['is_complex']:
                        Intent.objects.filter(name=validated_data['name'], agent=agent).delete()
                        raise serializers.ValidationError({'Erreur': [_("Vous devez verifier le type de reponse")]})
                    mixed_response = block_response_set.pop('mixed_response_set')
                    """"HERE######"""
                    blockResponse=None
                    for mixed_response_set in mixed_response:
                        if "simple_response_set" in block_response_set:
                            del block_response_set["simple_response_set"]
                        if not blockResponse:
                            try:
                                blockResponse= BlockResponse.objects.create(intent=intentObj,**block_response_set)
                            except:
                                Intent.objects.filter(name=validated_data['name'], agent=agent).delete()
                                raise serializers.ValidationError({'Erreur': [_("Vous devez specifier le type de reponse")]})
                        else:
                            pass

                        """creating the mixed response"""
                        if ((not ('image_set' in mixed_response_set)) or (not mixed_response_set['image_set'])) and \
                                ((not ('quick_reply_set' in mixed_response_set)) or (not mixed_response_set['quick_reply_set'])) and \
                                ((not ('gallery_set' in mixed_response_set)) or (not mixed_response_set['gallery_set'])) and \
                                ((not ('text_response_set' in mixed_response_set)) or (not mixed_response_set['text_response_set'])):
                            Intent.objects.filter(name=validated_data['name'], agent=agent).delete()
                            raise serializers.ValidationError({'Erreur': [_("Vous devez inserer au moin une reponse valide")]})
                        mixedResponse=MixedResponse.objects.create(block_response=blockResponse)

                        """Handling the image set"""
                        if ((('image_set' in mixed_response_set)) and (mixed_response_set['image_set'])):
                            image_set=mixed_response_set.pop('image_set')
                            #QuickReplySerializer.create(self,quick_reply_set, mixedResponse.id, agent.id, validated_data['name'])

                            for image in image_set:
                                if "imageName" in image and image["imageName"]:
                                    try:
                                        image_path = os.path.join(path_to_user_folder, 'images', str(image["imageName"]))
                                        del image["imageName"]
                                        image['image'] = File(open(image_path, 'rb'))
                                        Image.objects.create(mixed_response=mixedResponse, **image)
                                    except:
                                        Intent.objects.filter(name=validated_data['name'], agent=agent).delete()
                                        raise serializers.ValidationError(
                                            {'Erreur': [_("Vous devez verifier le contenue des images")]})

                                else:
                                    try:
                                        """convert the imagestr field to image field"""
                                        format, imgstr = image['imagestr'].split(';base64,')
                                        ext = format.split('/')[-1]
                                        imagefield = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
                                        req = image.copy()
                                        del req['imagestr']
                                        req['image'] = imagefield
                                        Image.objects.create(mixed_response=mixedResponse,**req)
                                    except:
                                        Intent.objects.filter(name=validated_data['name'], agent=agent).delete()
                                        raise serializers.ValidationError({'Erreur': [_("Vous devez verifier le contenue des images")]})

                        """Handling the Quick reply"""
                        if ((('quick_reply_set' in mixed_response_set)) and (mixed_response_set['quick_reply_set'])):
                            quick_reply_set = mixed_response_set.pop('quick_reply_set')
                            QuickReplySerializer.create(self,quick_reply_set, mixedResponse.id, agent.id, validated_data['name'])

                        """Handling the Quick reply"""
                        if ((('text_response_set' in mixed_response_set)) and (mixed_response_set['text_response_set'])):
                            text_response_set = mixed_response_set.pop('text_response_set')
                            TextResponseSerializer.create(self, text_response_set, mixedResponse.id, agent.id, validated_data['name'])

                        """Handling the gallery_set"""
                        if ((('gallery_set' in mixed_response_set)) and (mixed_response_set['gallery_set'])):
                            gallery_set = mixed_response_set.pop('gallery_set')

                            if path_to_user_folder is None:

                                GallerySerializer.create(self, gallery_set, mixedResponse.id, agent.id,
                                                         validated_data['name'])
                            else:
                                GallerySerializer.create(self, gallery_set, mixedResponse.id, agent.id,
                                                         validated_data['name'], path_to_user_folder)
        agent.status="non entrainer"
        agent.save()
        return intentObj

    def update(self, instance, validated_data):
        agentID = self.context['agentid']
        print("DATA", validated_data)

        """Delete _NOT YET TESTED"""


        if 'deleted' in validated_data and validated_data.get("deleted"):
            print("Some objects to delete")
            deleted = validated_data["deleted"][0]
            print("deleted :",  deleted)
            if "question_set" in deleted:
                question_set = deleted["question_set"]
                for id in question_set:
                    try:
                        question_obj = Question.objects.get(id=id)
                        question_obj.delete()
                    except Question.DoesNotExist:
                        print("Question not found")
            if "random_text_set" in deleted:
                random_text_set = deleted["random_text_set"]
                for id in random_text_set:
                    try:
                        random_text_obj = RandomText.objects.get(id=id)
                        random_text_obj.delete()
                    except RandomText.DoesNotExist:
                        print("Random text object not found")
            if "text_response_set" in deleted:
                text_response_set = deleted["text_response_set"]
                for id in text_response_set:
                    try:
                        text_response_obj = TextResponse.objects.get(id=id)
                        text_response_obj.delete()
                    except TextResponse.DoesNotExist:
                        print("Text Response object not found")
            if "gallery_set" in deleted:
                gallery_set = deleted["gallery_set"]
                for id in gallery_set:
                    try:
                        gallery_obj = Gallery.objects.get(id=id)
                        gallery_obj.delete()
                    except Gallery.DoesNotExist:
                        print("Gallery object not found")
            if "slider_set" in deleted:
                slider_set = deleted["slider_set"]
                for id in slider_set:
                    try:
                        slider_obj = Slider.objects.get(id=id)
                        slider_obj.delete()
                    except Slider.DoesNotExist:
                        print("Slider object not found")
            if "button_set" in deleted:
                button_set = deleted["button_set"]
                for id in button_set:
                    try:
                        button_obj = Button.objects.get(id=id)
                        button_obj.delete()
                    except Button.DoesNotExist:
                        print("Button object not found")
            if "image_set" in deleted:
                image_set = deleted["image_set"]
                for id in image_set:
                    try:
                        image_obj = Image.objects.get(id=id)
                        image_obj.delete()
                    except Image.DoesNotExist:
                        print("Image object not found")
            if "output_context_set" in deleted:
                output_context_set = deleted["output_context_set"]
                for id in output_context_set:
                    try:
                        output_context_obj = OutputContext.objects.get(id=id)
                        output_context_obj.delete()
                    except OutputContext.DoesNotExist:
                        print("OutputContext object not found")
            if "input_context_set" in deleted:
                input_context_set = deleted["input_context_set"]
                for id in input_context_set:
                    try:
                        input_context_obj = InputContext.objects.get(id=id)
                        input_context_obj.delete()
                    except InputContext.DoesNotExist:
                        print("InputContext object not found")

            if "quick_reply_set" in deleted:
                quick_reply_set = deleted["quick_reply_set"]
                for id in quick_reply_set:
                    try:
                        quick_reply_obj = QuickReply.objects.get(id=id)
                        quick_reply_obj.delete()
                    except QuickReply.DoesNotExist:
                        print("QuickReply object not found")
            if "related_entity_list" in deleted:
                entity = deleted["related_entity_list"]
                for id in entity:
                    try:
                        intObj = Entity_Intent.objects.get(id=id, intent = instance)
                        intObj.delete()
                    except Entity_Intent.DoesNotExist:
                        print("Entity to deleted does not exist")

            if "related_video_list" in deleted:
                video = deleted["related_video_list"]
                for id in video:
                    try:
                        videoObj = Video_Intent.objects.get(id=id, intent = instance)
                        video = videoObj.video
                        try:
                            [os.remove(video.video.path)]
                        except:
                            pass

                        videoObj.delete()
                        video.delete()
                    except Video_Intent.DoesNotExist:
                        print("Video to deleted does not exist")

            if "related_audio_list" in deleted:
                audio = deleted["related_audio_list"]
                for id in audio:
                    try:
                        audioObj = Audio_Intent.objects.get(id=id, intent = instance)
                        audio = audioObj.audio
                        try:
                            [os.remove(audio.audio.path)]
                        except:
                            pass
                        audioObj.delete()
                        audio.delete()
                    except Audio_Intent.DoesNotExist:
                        print("Audio to deleted does not exist")

            if "mixed_response_set" in deleted:
                mixed_response_set = deleted["mixed_response_set"]
                for mixed_response in mixed_response_set:
                    try:

                        repObj = MixedResponse.objects.filter(id=mixed_response).delete()

                    except MixedResponse.DoesNotExist:
                        pass
            if "block_response_set" in deleted:
                block_response_set = deleted["block_response_set"]
                for block_response in block_response_set:
                    try:
                        repObj = BlockResponse.objects.filter(id=block_response).delete()

                    except BlockResponse.DoesNotExist:
                        pass
            if "related_navigation_list" in deleted:
                related_navigation_list = deleted["related_navigation_list"]
                for navigation in related_navigation_list:
                    try:
                        repObj = NavigationIntent.objects.filter(id=navigation).delete()

                    except NavigationIntent.DoesNotExist:
                        pass
            if "related_depending_list" in deleted:
                related_depending_list = deleted["related_depending_list"]
                for depending in related_depending_list:
                    try:
                        repObj = DependingNavigation.objects.filter(id=depending).delete()

                    except DependingNavigation.DoesNotExist:
                        pass

        """End delete"""

        try:
            agent = Agent.objects.get(pk=agentID)
        except(TypeError, ValueError, OverflowError, Agent.DoesNotExist):
            raise serializers.ValidationError({'Erreur': [_("Cet agent n'existe pas")]})

        try:
            intentName=validated_data['name']
        except:
            raise serializers.ValidationError({'Erreur': [_("vous devez specifier le nom de l'intent à créer")]})
        instance.name = validated_data['name']
        if "fulfillment" in validated_data:
            instance.fulfillment = validated_data['fulfillment']
        if "description" in validated_data:
            instance.description = validated_data['description']
        instance.save()

        """Handling entitys"""
        if 'related_entity_list' in validated_data:
            entity = validated_data.pop('related_entity_list')
            update = IntentEntityManagerSerializer.update(self, entity, instance)

        """Handling entitys"""
        if 'related_navigation_list' in validated_data:
            navigation = validated_data.pop('related_navigation_list')
            update = NavigationIntentManagerSerialiser.update(self, navigation, instance)

        """Handling videos"""
        if 'related_video_list' in validated_data:
            videos = validated_data.pop('related_video_list')
            update = IntentVideoManagerSerializer.update(self, videos, instance)

        """Handling Audios"""
        if 'related_audio_list' in validated_data:
            audios = validated_data.pop('related_audio_list')
            update = IntentAudioManagerSerializer.update(self, audios, instance)



        """Handling the input context set"""
        if 'input_context_set' in validated_data and validated_data['input_context_set']:
            input_context_set = validated_data.pop('input_context_set')
            intentList = Intent.objects.filter(agent=agent)
            for incontext in input_context_set:
                if 'id' in incontext and incontext['id']:
                    inContextInstance= InputContext.objects.get(id = incontext['id'])
                    relatedOutContext = OutputContext.objects.get(id=incontext["outContextID"])

                    inContextInstance.outContext = relatedOutContext
                    inContextInstance.save()
                else:
                    existOutputContext = OutputContext.objects.filter(id=incontext["outContextID"],
                                                                      intent__in=intentList)
                    if len(existOutputContext) > 0:
                        try:
                            relatedOutContext = OutputContext.objects.get(id=incontext["outContextID"])
                            input_context_obj = InputContext.objects.create(intent=instance,
                                                                            outContext=relatedOutContext)
                            instance.date_update = timezone.now()
                            instance.save()
                        except:
                            raise serializers.ValidationError(
                                {'Erreur': [_("erreur lors de l'insertion des input context")]})
                    else:
                        raise serializers.ValidationError(
                            {'Erreur': [_(
                                "Vous devez inserer un input context referencier pour un output context deja existant et appartient au meme agent")]})

        """Handling the output_context_set"""
        if 'output_context_set' in validated_data and validated_data["output_context_set"]:
            output_context_set = validated_data.pop('output_context_set')
            intentList = Intent.objects.filter(agent = agent)

            for outcontext in output_context_set:
                if 'id' in outcontext and outcontext['id'] :
                    output_context_temp = OutputContext.objects.get (id=outcontext['id'])
                    output_context_temp.outContext = outcontext['outContext']
                    output_context_temp.save()
                else:
                    try:
                        verif = OutputContext.objects.get(outContext = outcontext['outContext'], intent__in =intentList)
                    except:
                        verif = None
                    if not verif:
                        OutputContext.objects.create(intent = instance, **outcontext)
        """Handling the question_set"""
        if 'question_set' in validated_data and validated_data['question_set']:
            question_set = validated_data.pop('question_set')
            for question in question_set:
                if 'id' in question and question['id']:
                    questionTemp=Question.objects.get(id=question['id'])
                    questionTemp.name=question['name']
                    questionTemp.save()
                else:
                    try:
                        Question.objects.create(intent=instance, **question)
                    except:
                        raise serializers.ValidationError({'Erreur': [_("erreur lors de l'insertion des questions")]})

        """Handling the bloc response set"""
        block_response=None
        fulfillment=None
        if 'fulfillment' in validated_data:
            fulfillment=validated_data['fulfillment']
        if 'block_response_set' in validated_data and validated_data['block_response_set']:
            block_response = validated_data.pop('block_response_set')
        if not block_response and not fulfillment:
            raise serializers.ValidationError({'Erreur': [_("Vous devez specifier une reponse")]})
        if block_response:
            for block_response_set in block_response:

                if ('simple_response_set' in block_response_set and block_response_set['simple_response_set']) and ('mixed_response_set' in block_response_set and block_response_set['mixed_response_set']):
                    raise serializers.ValidationError({'Erreur': [_("Vous devez specifier un seul type de reponse")]})

                """Handling the simple response"""
                if ('simple_response_set' in block_response_set ):
                    if 'is_complex' in block_response_set and block_response_set['is_complex']:
                        raise serializers.ValidationError({'Erreur': [_("Vous devez verifier le type de reponse")]})
                    simple_response_set = block_response_set.pop('simple_response_set')[0]

                    if 'id' in block_response_set:
                        blockResponse = BlockResponse.objects.get(id=block_response_set['id'])
                        if blockResponse.is_complex != block_response_set['is_complex']:

                            if blockResponse.is_complex:
                                blockResponse.mixed_response_set.all().delete()
                            else:
                                blockResponse.simple_response_set.all().delete()
                            blockResponse.is_complex = block_response_set['is_complex']
                            blockResponse.save()


                    if 'id' in simple_response_set:
                        blockResponse = BlockResponse.objects.get(id = block_response_set['id'])
                        blockResponse.is_complex=block_response_set['is_complex']
                        blockResponse.save()
                    elif not 'id' in block_response_set:
                        try:
                            blockResponse = BlockResponse.objects.create(intent=instance, **block_response_set)
                        except:
                            raise serializers.ValidationError({'Erreur': [_("Vous devez specifier le type de reponse")]})

                    """Handling the random text set"""
                    if (not ('random_text_set' in simple_response_set)) or (not simple_response_set['random_text_set']) or ('id' in simple_response_set and not 'id' in block_response_set):
                        raise serializers.ValidationError({'Erreur': [_("Vous devez inserer des reponses valides")]})

                    if 'id' in simple_response_set:
                        simpleResponse = SimpleResponse.objects.get(id = simple_response_set['id'])
                    else:
                        try:
                            SimpleResponse.objects.filter(block_response=blockResponse.id).delete()
                        except:
                            pass
                        try:
                            simpleResponse = SimpleResponse.objects.create(block_response=blockResponse)
                        except:
                            raise serializers.ValidationError({'Erreur': [_("Vous devez specifier le type de reponse")]})


                    """Handling the random text of simple response"""
                    random_text_set = simple_response_set.pop('random_text_set')
                    for text in random_text_set:
                        if 'id' in text and not 'id' in simple_response_set:
                            raise serializers.ValidationError(
                                {'Erreur': [_("verifier le contenue de random_text_reponse")]})
                        try:
                            if 'id' in text:
                                txttemp=RandomText.objects.get(id=text['id'])
                                txttemp.name = text['name']
                                txttemp.order = text['order']
                                txttemp.save()
                            else:
                                RandomText.objects.create(simple_response=simpleResponse, **text)
                        except:
                            raise serializers.ValidationError(
                                {'Erreur': [_("Vous devez verifier le contenue de random_text_reponse")]})

                """Handling the mixed response"""
                if ('mixed_response_set' in block_response_set and block_response_set['mixed_response_set']):
                    if 'is_complex' in block_response_set and not block_response_set['is_complex']:
                        raise serializers.ValidationError({'Erreur': [_("Vous devez verifier le type de reponse")]})
                    mixed_response = block_response_set.pop('mixed_response_set')

                    if 'id' in block_response_set:
                        blockResponse = BlockResponse.objects.get(id=block_response_set['id'])
                        if blockResponse.is_complex != block_response_set['is_complex']:

                            if blockResponse.is_complex:
                                blockResponse.mixed_response_set.all().delete()
                            else:
                                blockResponse.simple_response_set.all().delete()
                            blockResponse.is_complex = block_response_set['is_complex']
                            blockResponse.save()



                    else:

                        # BlockResponse.objects.filter(intent=instance).delete()
                        try:
                            blockResponse = BlockResponse.objects.create(intent=instance, **block_response_set)
                        except:
                            raise serializers.ValidationError({'Erreur': [_("Vous devez specifier le type de reponse")]})

                    for mixed_response_set in mixed_response:
                        """creating the mixed response"""
                        if 'id' in mixed_response_set:
                            blockResponse = BlockResponse.objects.get(id = block_response_set['id'])
                            blockResponse.is_complex=block_response_set['is_complex']
                            blockResponse.save()

                        if ((not ('image_set' in mixed_response_set)) or (not mixed_response_set['image_set'])) and \
                                ((not ('quick_reply_set' in mixed_response_set)) or (not mixed_response_set['quick_reply_set'])) and \
                                ((not ('gallery_set' in mixed_response_set)) or (not mixed_response_set['gallery_set'])) and \
                                ((not ('text_response_set' in mixed_response_set)) or (
                                        not mixed_response_set['text_response_set'])):
                            raise serializers.ValidationError({'Erreur': [_("Vous devez inserer au moin une reponse valide")]})

                        if 'id' in mixed_response_set and not 'id' in block_response_set:
                            raise serializers.ValidationError({'Erreur': [_("impossible de modifier un objet mixed response appartenant à un nouveau objet response")]})

                        if 'id' in mixed_response_set:
                            mixedResponse = MixedResponse.objects.get(id = mixed_response_set['id'])
                        else:
                            # try:
                            #     #TODO must be tested to check if it affect the images
                            #     MixedResponse.objects.filter(block_response=blockResponse.id).delete()
                            # except:
                            pass
                            try:
                                mixedResponse = MixedResponse.objects.create(block_response=blockResponse)
                            except:
                                raise serializers.ValidationError({'Erreur': [_("Vous devez specifier le type de reponse")]})



                        """Handling the image set"""
                        if ((('image_set' in mixed_response_set)) and (mixed_response_set['image_set'])):
                            image_set = mixed_response_set.pop('image_set')
                            # QuickReplySerializer.create(self,quick_reply_set, mixedResponse.id, agent.id, validated_data['name'])

                            for image in image_set:
                                if 'imagestr' in image and image['imagestr'] and not 'id' in image:
                                    try:
                                        """convert the imagestr field to image field"""
                                        format, imgstr = image['imagestr'].split(';base64,')
                                        ext = format.split('/')[-1]
                                        imagefield = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
                                        req = image.copy()
                                        del req['imagestr']
                                        if 'id' in req:
                                            del req['id']
                                        req['image'] = imagefield
                                        Image.objects.create(mixed_response=mixedResponse, **req)
                                    except:
                                        raise serializers.ValidationError({'Erreur': [_("Vous devez verifier le contenue des images")]})

                                elif 'imagestr' in image and image['imagestr'] and 'id' in image:
                                    try:
                                        """convert the imagestr field to image field"""
                                        format, imgstr = image['imagestr'].split(';base64,')
                                        ext = format.split('/')[-1]
                                        imagefield = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
                                        field=Image.objects.get(id=image['id'])

                                        field.image = imagefield
                                        field.order = image['order']
                                        field.save()

                                    except:
                                        raise serializers.ValidationError({'Erreur': [_("Vous devez verifier le contenue des images")]})

                                elif 'imageurl' in image and image['imageurl'] and 'id' in image and image['id']:
                                    try:
                                        req = Image.objects.get(id = image['id'])
                                        req.order = image['order']
                                        req.save()
                                    except:
                                        raise serializers.ValidationError({'Erreur': [_("Vous devez verifier le contenue des images ")]})


                        """Handling the Quick reply"""
                        if ((('quick_reply_set' in mixed_response_set)) and (mixed_response_set['quick_reply_set'])):
                            quick_reply_set = mixed_response_set.pop('quick_reply_set')
                            QuickReplySerializer.update(self, instance, quick_reply_set, mixedResponse.id, agent.id, validated_data['name'])

                        """Handling the text response"""
                        if ((('text_response_set' in mixed_response_set)) and (mixed_response_set['text_response_set'])):
                            text_response_set = mixed_response_set.pop('text_response_set')
                            TextResponseSerializer.update(self, instance, text_response_set, mixedResponse.id, agent.id,
                                                          validated_data['name'])

                        """Handling the gallery_set"""
                        if ((('gallery_set' in mixed_response_set)) and (mixed_response_set['gallery_set'])):
                            gallery_set = mixed_response_set.pop('gallery_set')
                            GallerySerializer.update(self, instance, gallery_set, mixedResponse.id, agent.id,
                                                     validated_data['name'])


        agent.status = "non entrainer"
        agent.save()
        return Response({"success":True})

class IntentSerializer(serializers.ModelSerializer):
    question_set = QuestionSerializer(many=True, required=False)
    block_response_set = BlockResponseSerializer(many=True, required=False)
    agent_id = serializers.IntegerField(required=True)
    deleted = serializers.JSONField(required=False)
    #
    output_context_set = OutputContextSerializer(many=True, required=False)
    input_context_set = InputContextSerializer(many=True, required=False)
    is_complex = serializers.BooleanField(required=False)
    class Meta:
        model = Intent
        fields = ['id', 'name', 'agent_id', 'date_create', 'date_update', 'question_set', 'block_response_set',
                  'deleted', 'is_complex', 'output_context_set','input_context_set']

    def create(self, validated_data):
        print("validated data :", validated_data)
        test_block_response = False
        test_mixed_response = False

        intent = validated_data.get('name')
        agent_id = validated_data.get("agent_id")
        is_complex = validated_data.get("is_complex")
        print("is complex :", is_complex)

        try:
            agent = Agent.objects.get(id=agent_id)
        except Exception as AgentNotFound:
            print("Agent Not Found")
            raise serializers.ValidationError({"erreur": "Agent non reconnue."})

        exist = Intent.objects.filter(name=intent, agent=agent)
        if exist:
            print("intent with this name already exist")
            raise serializers.ValidationError({"erreur": "Le nom de l'intent est deja utilisée. veuillez utilser un autre"})
        else:
            intent_obj = Intent.objects.create(name=intent, agent=agent)

        """Input/Output Context"""

        if 'output_context_set' in validated_data and validated_data.get("output_context_set"):
            output_context_set = validated_data.pop('output_context_set')

            intent_ids = [intent.id for intent in Intent.objects.filter(agent=agent)]
            for output_context in output_context_set:

                output_context_obj = OutputContext.objects.filter(outContext=output_context["outContext"],
                                                                   intent__in=intent_ids)
                if len(output_context_obj)>0:
                    Intent.objects.filter(id=intent_obj.id).delete()
                    # #intent_obj.delete()
                    # import pprint
                    # print('egaliter',intent_obj)
                    raise serializers.ValidationError({"erreur": "Cet output context est deja existant, veuillez utlizer un autre"})

                out_context_obj = OutputContext.objects.create(**output_context, intent=intent_obj)
        if 'input_context_set' in validated_data and validated_data.get("input_context_set"):
            input_context_set = validated_data.pop('input_context_set')
            for input_context in input_context_set:
                # TODO : create input context and associate it to
                input_context_obj = InputContext.objects.create(intent=intent_obj,
                                                                outContext=input_context["outContext"])

        """End Output Context"""

        try:
            questions = validated_data.pop('question_set')
            print("question_set :", questions)
            if questions:
                for question in questions:
                    Question.objects.create(**question, intent=intent_obj)
        except:
            print("No questions")

        if 'block_response_set' in validated_data and validated_data.get("block_response_set"):
            block_response = validated_data.get("block_response_set")[0]
            print("block response :", block_response)
            # TODO : find mixed response set
            if "mixed_response_set" in block_response and block_response.get("mixed_response_set"):
                mixed_response = block_response.pop("mixed_response_set")[0]
                print("mixed response :", mixed_response)
                # TODO : text_response_set
                if "text_response_set" in mixed_response and mixed_response.get("text_response_set"):
                    text_response_set = mixed_response.pop("text_response_set")
                    print("text_response_set :", text_response_set)
                    for text_response in text_response_set:
                        # TODO : create block response and mixed response objects
                        if not test_block_response:
                            block_response_obj = BlockResponse.objects.create(intent=intent_obj, is_complex=is_complex)
                            test_block_response = True
                        if not test_mixed_response:
                            mixed_response_obj = MixedResponse.objects.create(block_response=block_response_obj)
                            test_mixed_response = True
                        # TODO : create url button object
                        text_obj = TextResponse.objects.create(name=text_response["name"], order=text_response["order"],
                                                               mixed_response=mixed_response_obj)
                        if "button_set" in text_response and text_response.get("button_set"):
                            buttons = text_response.pop("button_set")
                            print("buttons :", buttons)
                            for button in buttons:
                                Button.objects.create(**button, text_response=text_obj)
                # TODO : quick replies set
                if "quick_reply_set" in mixed_response and mixed_response.get("quick_reply_set"):
                    quick_reply_set = mixed_response.pop("quick_reply_set")
                    print("quick_reply_set :", quick_reply_set)

                    for quick_reply in quick_reply_set:
                        if "button_set" in quick_reply and quick_reply.get("button_set"):
                            buttons = quick_reply.pop("button_set")
                            print("buttons :", buttons)
                            # TODO : create block response and mixed response objects
                            if not test_block_response:
                                block_response_obj = BlockResponse.objects.create(intent=intent_obj, is_complex=is_complex)
                                test_block_response = True
                            if not test_mixed_response:
                                mixed_response_obj = MixedResponse.objects.create(block_response=block_response_obj)
                                test_mixed_response = True
                            # TODO : create quick reply object
                            quick_reply_obj = QuickReply.objects.create(**quick_reply,
                                                                        mixed_response=mixed_response_obj)
                            for button in buttons:
                                button["payload"] = button["name"]
                                Button.objects.create(**button, quick_reply=quick_reply_obj)
                # TODO : gallery set
                if "gallery_set" in mixed_response and mixed_response.get("gallery_set"):
                    gallery_set = mixed_response.pop("gallery_set")
                    print("gallery_set :", gallery_set)

                    for gallery in gallery_set:
                        print("gallery :", gallery)
                        if "slider_set" in gallery and gallery.get("slider_set"):
                            sliders = gallery.pop("slider_set")
                            print("sliders :", sliders)
                            # TODO : create block response and mixed response objects
                            if not test_block_response:
                                block_response_obj = BlockResponse.objects.create(intent=intent_obj, is_complex=is_complex)
                                test_block_response = True
                            if not test_mixed_response:
                                mixed_response_obj = MixedResponse.objects.create(block_response=block_response_obj)
                                test_mixed_response = True
                            # TODO : create gallery object
                            gallery_obj = Gallery.objects.create(**gallery, mixed_response=mixed_response_obj)
                            # TODO : create sliders associated to gallery
                            for slider in sliders:
                                print("slider :", slider)
                                if "button_set" in slider:
                                    buttons = slider.pop("button_set")
                                    test_btn_slider = True
                                    print("button of slider :", buttons)
                                slider_obj = Slider.objects.create(**slider, gallery=gallery_obj)
                                if test_btn_slider:
                                    # buttons = slider.pop("button_set")
                                    for button in buttons:
                                        print("btn :", button)
                                        Button.objects.create(**button, slider=slider_obj)
                # TODO : image set
                if "image_set" in mixed_response and mixed_response.get("image_set"):
                    image_set = mixed_response.pop("image_set")
                    print("image_set :", image_set)
                    # TODO : create block response and mixed response objects
                    if not test_block_response:
                        block_response_obj = BlockResponse.objects.create(intent=intent_obj, is_complex=is_complex)
                        test_block_response = True
                    if not test_mixed_response:
                        mixed_response_obj = MixedResponse.objects.create(block_response=block_response_obj)
                        test_mixed_response = True
                    for image in image_set:
                        print("image :", image)
                        # TODO : create image object
                        image_obj = Image.objects.create(image=image["image"], order=image["order"], mixed_response=mixed_response_obj)
            # TODO : find simple response set
            if "simple_response_set" in block_response and block_response.get("simple_response_set"):
                simple_response = block_response.pop("simple_response_set")[0]
                print("yes got simple responses")
                print("simple response :", simple_response)
                # TODO : random_text_set
                if "random_text_set" in simple_response and simple_response.get("random_text_set"):
                    random_text_set = simple_response.pop("random_text_set")
                    print("random_text_set :", random_text_set)
                    # TODO : create block response and mixed response objects
                    if not test_block_response:
                        block_response_obj = BlockResponse.objects.create(intent=intent_obj, is_complex=is_complex)
                        test_block_response = True
                    # TODO : create simple response object
                    simple_response_obj = SimpleResponse.objects.create(block_response=block_response_obj)
                    # TODO : create random text response objects
                    for random_text in random_text_set:
                        print("random_text :", random_text)
                        RandomText.objects.create(**random_text, simple_response=simple_response_obj)

        else:
            print("No Block responses")

        return intent_obj

    def update(self, instance, validated_data):

        print("Validated data received in update intent serializer method :", validated_data)
        is_complex = validated_data.get('is_complex')
        print("is complex in update :", is_complex)
        # TODO : catch does not exist intent name exception that may raise
        try:
            intent_name = validated_data.get('name')
            print("intent name :", intent_name)
        except Exception as e:
            raise serializers.ValidationError({"intent": "This field is required."})

        # TODO : modify the intent name if edited
        print("instance agent :", instance.agent)
        exist = Intent.objects.filter(name=intent_name, agent=instance.agent)
        print("exist :", exist)
        print("len exist :", len(exist))

        if len(exist) == 0:
            instance.name = validated_data.get('name', instance.name)
            instance.save()
        if len(exist) == 1:
            if exist[0].name == instance.name:
                pass
            else:
                print("intent with this name already exist")
                raise serializers.ValidationError({"intent_exist": "Intent with this name already exists."})

        """Input/Output Context"""

        if 'output_context_set' in validated_data and validated_data.get("output_context_set"):
            output_context_set = validated_data.pop('output_context_set')

            intent_ids = [intent.id for intent in Intent.objects.filter(agent=instance.agent)]
            for output_context in output_context_set:

                output_context_obj = OutputContext.objects.filter(outContext=output_context["outContext"],
                                                                   intent__in=intent_ids)
                if len(output_context_obj)>0:
                    raise serializers.ValidationError({"output_context": output_context["outContext"]})

                out_context_obj = OutputContext.objects.create(**output_context, intent=instance)
        if 'input_context_set' in validated_data and validated_data.get("input_context_set"):
            input_context_set = validated_data.pop('input_context_set')
            for input_context in input_context_set:
                # TODO : create input context and associate it to
                input_context_obj = InputContext.objects.create(intent=instance,
                                                                outContext=input_context["outContext"])

        """End Input/Output Context"""

        # TODO : question_set
        try:
            questions = validated_data.pop('question_set')
            print("question_set update :", questions)
            # get all nested objects related with this instance and make a dict(id, object)

            for question in questions:
                print("question :", question)
                if question["id"] != 0:
                    print("question exists !")
                    question_id = question["id"]
                    print("question id :", question_id)

                    try:
                        question_obj = Question.objects.get(id=question_id, intent=instance)
                        print(question_obj)
                        question_obj.name = question['name']
                        question_obj.order = question['order']
                        question_obj.save()
                    except Question.DoesNotExist:
                        raise serializers.ValidationError({"intent_exist": "question with id " + str(question_id) + " not found."})

                else:
                    print("new question")
                    Question.objects.create(intent=instance, name=question["name"], order=question["order"])

        except Exception as e:
            print("No questions")
            print(e)

        # TODO : block response set
        if 'block_response_set' in validated_data and validated_data.get("block_response_set"):
            block_response = validated_data.get("block_response_set")[0]
            print("block response :", block_response)
            print("block response id :", block_response["id"])
            block_response_id = block_response["id"]
            if block_response_id == 0:
                test_block_response = False
            else:
                print("block response exists ++++++++++++++")
                try:
                    block_response_obj = BlockResponse.objects.get(id=block_response_id, intent=instance)
                except(TypeError, ValueError, OverflowError, BlockResponse.DoesNotExist):
                    raise serializers.ValidationError(
                        {"error": "The BlockResponse with id " + str(block_response_id)+ " does not exist"})

                complex_type = block_response_obj.is_complex
                print(complex_type)
                # TODO : before updating the is_complex field in the block response object we have to check if
                if complex_type == is_complex:
                    print("the type of the response has not changed")
                else:
                    print("soit la réponse était simple est devenu nested soit l'inverse ----------------------------")
                    # TODO : soit supprimer les réponses simples soit les réponses composés
                    if is_complex:
                        simple_responses_queryset = SimpleResponse.objects.filter(block_response=block_response_obj)
                        for simple in simple_responses_queryset:
                            simple.delete()

                    else:
                        mixed_response_queryset = MixedResponse.objects.filter(block_response=block_response_obj)
                        for mixed in mixed_response_queryset:
                            mixed.delete()
                        print("complete deleting nested responses *****************")
                # TODO : update block response is_complex field
                block_response_obj.is_complex = is_complex
                block_response_obj.save()
                print("++++++++++++++")
                test_block_response = True
            # TODO : find simple response set
            if "simple_response_set" in block_response and block_response.get("simple_response_set"):
                simple_response = block_response.pop("simple_response_set")[0]
                print("yes got simple responses")
                print("simple response :", simple_response)
                simple_response_id = simple_response["id"]
                if simple_response_id == 0:
                    test_simple_response = False
                else:
                    simple_response_obj = SimpleResponse.objects.get(id=simple_response_id, block_response=block_response_obj)
                    test_simple_response = True
                print("simple response id :", simple_response_id)
                # TODO : random_text_set
                if "random_text_set" in simple_response and simple_response.get("random_text_set"):
                    random_text_set = simple_response.pop("random_text_set")
                    print("random_text_set :", random_text_set)
                    for random_text in random_text_set:
                        print("random text :", random_text)
                        if random_text["id"] != 0:
                            print("modify existing random text object")
                            try:
                                random_text_obj = RandomText.objects.get(id=random_text["id"])
                                random_text_obj.name = random_text["name"]
                                random_text_obj.order = random_text["order"]
                                random_text_obj.save()
                            except Exception as RandomTextDoesNotExist:
                                print("Random text object does not exist.")
                        else:
                            print("create new random text")
                            # TODO : what if the intent to update has no block response obj and/or no simple response obj before : we have to check this case
                            if not test_block_response:
                                # TODO : create a block response object
                                block_response_obj = BlockResponse.objects.create(intent=instance, is_complex=is_complex)
                                test_block_response = True
                            if not test_simple_response:
                                simple_response_obj = SimpleResponse.objects.create(block_response=block_response_obj)
                                test_simple_response = True
                            random_text_obj = RandomText.objects.create(name=random_text["name"], order=random_text["order"], simple_response=simple_response_obj)
            # TODO : find mixed response set
            if "mixed_response_set" in block_response and block_response.get("mixed_response_set"):
                mixed_response = block_response.pop("mixed_response_set")[0]
                print("mixed response :", mixed_response)
                mixed_response_id = mixed_response["id"]
                print("mixed response id :", mixed_response_id)
                if mixed_response_id == 0:
                    test_mixed_response = False
                else:
                    mixed_response_obj = MixedResponse.objects.get(id=mixed_response_id, block_response=block_response_obj)
                    test_mixed_response = True
                # TODO : text_response_set
                if "text_response_set" in mixed_response and mixed_response.get("text_response_set"):
                    text_response_set = mixed_response.pop("text_response_set")
                    print("text_response_set :", text_response_set)
                    for text_response in text_response_set:
                        if text_response["id"] != 0:
                            print("modifying existing text_response")
                            text_obj = TextResponse.objects.get(id=text_response["id"])
                            text_obj.name = text_response["name"]
                            text_obj.order = text_response["order"]
                            text_obj.save()
                            # TODO : button_set
                            if "button_set" in text_response and text_response["button_set"]:
                                button_set = text_response["button_set"]
                                for button in button_set:
                                    if button["id"] != 0:
                                        print("modifying existing button in text response")
                                        button_obj = Button.objects.get(id=button["id"])
                                        button_obj.name = button["name"]
                                        button_obj.url = button["url"]
                                        button_obj.order = button["order"]
                                        button_obj.save()
                                    else:
                                        print("creating new button to existing text response")
                                        button_obj = Button.objects.create(name=button["name"], order=button["order"], url=button["url"], text_response=text_obj)
                        else:
                            print("creating new text response objects")
                            if not test_block_response:
                                # TODO : create a block response object
                                block_response_obj = BlockResponse.objects.create(intent=instance, is_complex=is_complex)
                                test_block_response = True
                            if not test_mixed_response:
                                mixed_response_obj = MixedResponse.objects.create(block_response=block_response_obj)
                                test_mixed_response = True
                            text_obj = TextResponse.objects.create(name=text_response["name"], order=text_response["order"], mixed_response=mixed_response_obj)
                            if "button_set" in text_response and text_response["button_set"]:
                                button_set = text_response["button_set"]
                                # TODO : create buttons
                                for button in button_set:
                                    Button.objects.create(name=button["name"], order=button["order"], url=button["url"], text_response=text_obj)
                # TODO : image set
                if "image_set" in mixed_response and mixed_response.get("image_set"):
                    image_set = mixed_response.pop("image_set")
                    print("image_set :", image_set)
                    for image in image_set:
                        print("image :", image)
                        if image["id"] != 0:
                            print("modifying existing image")
                            image_obj = Image.objects.get(id=image["id"])
                            image_obj.image = image["image"]
                            image_obj.order = image["order"]
                            image_obj.save()
                        else:
                            print("creating new image")
                            if not test_block_response:
                                # TODO : create a block response object
                                block_response_obj = BlockResponse.objects.create(intent=instance, is_complex=is_complex)
                                test_block_response = True
                            if not test_mixed_response:
                                mixed_response_obj = MixedResponse.objects.create(block_response=block_response_obj)
                                test_mixed_response = True
                            image_obj = Image.objects.create(image=image["image"], order=image["order"], mixed_response=mixed_response_obj)
                # TODO : quick reply objects set
                if "quick_reply_set" in mixed_response and mixed_response.get("quick_reply_set"):
                    quick_reply_set = mixed_response.pop("quick_reply_set")
                    print("quick_reply_set :", quick_reply_set)
                    for quick_reply in quick_reply_set:
                        if "button_set" in quick_reply and quick_reply.get("button_set"):
                            buttons = quick_reply.pop("button_set")
                            if quick_reply["id"] != 0:
                                print("modifying existing quick reply")
                                quick_reply_obj = QuickReply.objects.get(id=quick_reply["id"])
                                quick_reply_obj.name = quick_reply["name"]
                                quick_reply_obj.order = quick_reply["order"]
                                quick_reply_obj.save()
                                for button in buttons:
                                    if button["id"] != 0:
                                        print("update button")
                                        button_obj = Button.objects.get(id=button["id"])
                                        button_obj.name = button["name"]
                                        button_obj.payload = button["name"]
                                        button_obj.order = button["order"]
                                        button_obj.save()
                                    else:
                                        print(" create new button")
                                        Button.ojects.create(name=button["name"], payload=button["name"], order=button["order"], quick_reply=quick_reply_obj)
                            else:
                                print("create new quick reply")
                                if "button_set" in quick_reply and quick_reply.get("button_set"):
                                    buttons = quick_reply.pop("button_set")
                                    if not test_block_response:
                                        # TODO : create a block response object
                                        block_response_obj = BlockResponse.objects.create(intent=instance, is_complex=is_complex)
                                        test_block_response = True
                                    if not test_mixed_response:
                                        mixed_response_obj = MixedResponse.objects.create(block_response=block_response_obj)
                                        test_mixed_response = True
                                    quick_reply_obj = QuickReply.objcets.create(name=quick_reply["name"], order=quick_reply["order"], mixed_response=mixed_response_obj)
                                    for button in buttons:
                                        Button.ojects.create(name=button["name"], payload=button["name"],
                                                             order=button["order"], quick_reply=quick_reply_obj)
                # TODO : gallery set
                if "gallery_set" in mixed_response and mixed_response.get("gallery_set"):
                    gallery_set = mixed_response.pop("gallery_set")
                    print("gallery_set :", gallery_set)
                    for gallery in gallery_set:
                        print("gallery :", gallery)
                        if gallery["id"] != 0:
                            print("modifying existing gallery")
                            gallery_obj = Gallery.objects.get(id=gallery["id"])
                            gallery_obj.order = gallery["order"]
                            gallery_obj.save()
                            if "slider_set" in gallery and gallery.get("slider_set"):
                                slider_set = gallery.pop("slider_set")
                                print("sliders :", slider_set)
                                for slider in slider_set:
                                    if slider["id"] != 0:
                                        print("modifying existing slider")
                                        slider_obj = Slider.objects.get(id=slider["id"])
                                        slider_obj.image = slider["image"]
                                        slider_obj.title = slider["title"]
                                        slider_obj.subtitle = slider["subtitle"]
                                        slider_obj.url = slider["url"]
                                        slider_obj.order = slider["order"]
                                        if "button_set" in slider and slider["button_set"]:
                                            button_set = slider.pop("button_set")
                                            for button in button_set:
                                                print("button :", button)
                                                if button["id"] != 0:
                                                    print("modifying existing button in slider")
                                                    button_obj = Button.objects.get(id=button["id"])
                                                    button_obj.name = button["name"]
                                                    button_obj.url = button["url"]
                                                    button_obj.order = button["order"]
                                                    button_obj.save()
                                                else:
                                                    print("creating new button in existing slider")
                                                    Button.objects.create(name=button["name"], url=button["url"], order=button["order"])
                                    else:
                                        print("creating new slider in existing gallery")
                                        slider_obj = Slider.objects.create(gallery=gallery_obj, image=slider["image"],
                                                                           title=slider["title"], subtitle=slider["subtitle"],
                                                                           url=slider["url"], order=slider["order"])
                                        if "button_set" in slider and slider["button_set"]:
                                            button_set = slider.pop("button_set")
                                            for button in button_set:
                                                print("button :", button)
                                                Button.objects.create(name=button["name"], url=button["url"],
                                                                       order=button["order"], slider=slider_obj)

                        else:
                            print("creating new gallery")
                            if not test_block_response:
                                # TODO : create a block response object
                                block_response_obj = BlockResponse.objects.create(intent=instance, is_complex=is_complex)
                                test_block_response = True
                            if not test_mixed_response:
                                mixed_response_obj = MixedResponse.objects.create(block_response=block_response_obj)
                                test_mixed_response = True
                                gallery_obj = Gallery.objects.create(order=gallery["order"], mixed_response=mixed_response_obj)
                                if "slider_set" in gallery and gallery["slider_set"]:
                                    slider_set = gallery["slider_set"]
                                    for slider in slider_set:
                                        print("slider :", slider)
                                        slider_obj = Slider.objects.create(gallery=gallery_obj, image=slider["image"],
                                                                           title=slider["title"],
                                                                           subtitle=slider["subtitle"],
                                                                           url=slider["url"], order=slider["order"])
                                        if "button_set" in slider and slider["button_set"]:
                                            button_set = slider.pop("button_set")
                                            for button in button_set:
                                                print("button :", button)
                                                Button.objects.create(name=button["name"], url=button["url"],
                                                                      order=button["order"], slider=slider_obj)
        if 'deleted' in validated_data and validated_data.get("deleted"):
            print("Some objects to delete")
            deleted = validated_data["deleted"][0]
            print("deleted :",  deleted)
            if "question_set" in deleted:
                question_set = deleted["question_set"]
                for id in question_set:
                    try:
                        question_obj = Question.objects.get(id=id)
                        question_obj.delete()
                    except Question.DoesNotExist:
                        print("Question not found")
            if "random_text_set" in deleted:
                random_text_set = deleted["random_text_set"]
                for id in random_text_set:
                    try:
                        random_text_obj = RandomText.objects.get(id=id)
                        random_text_obj.delete()
                    except RandomText.DoesNotExist:
                        print("Random text object not found")
            if "text_response_set" in deleted:
                text_response_set = deleted["text_response_set"]
                for id in text_response_set:
                    try:
                        text_response_obj = TextResponse.objects.get(id=id)
                        text_response_obj.delete()
                    except TextResponse.DoesNotExist:
                        print("Text Response object not found")
            if "gallery_set" in deleted:
                gallery_set = deleted["gallery_set"]
                for id in gallery_set:
                    try:
                        gallery_obj = Gallery.objects.get(id=id)
                        gallery_obj.delete()
                    except Gallery.DoesNotExist:
                        print("Gallery object not found")
            if "slider_set" in deleted:
                slider_set = deleted["slider_set"]
                for id in slider_set:
                    try:
                        slider_obj = Slider.objects.get(id=id)
                        slider_obj.delete()
                    except Slider.DoesNotExist:
                        print("Slider object not found")
            if "button_set" in deleted:
                button_set = deleted["button_set"]
                for id in button_set:
                    try:
                        button_obj = Button.objects.get(id=id)
                        button_obj.delete()
                    except Button.DoesNotExist:
                        print("Button object not found")
            if "image_set" in deleted:
                image_set = deleted["image_set"]
                for id in image_set:
                    try:
                        image_obj = Image.objects.get(id=id)
                        image_obj.delete()
                    except Image.DoesNotExist:
                        print("Image object not found")
            if "output_context_set" in deleted:
                output_context_set = deleted["output_context_set"]
                for id in output_context_set:
                    try:
                        output_context_obj = OutputContext.objects.get(id=id)
                        output_context_obj.delete()
                    except OutputContext.DoesNotExist:
                        print("OutputContext object not found")
            if "input_context_set" in deleted:
                input_context_set = deleted["input_context_set"]
                for id in input_context_set:
                    try:
                        input_context_obj = InputContext.objects.get(id=id)
                        input_context_obj.delete()
                    except InputContext.DoesNotExist:
                        print("InputContext object not found")

        return instance

class Exempleserializer(serializers.Serializer):
    """Class serializer for log in"""

    agent_id = serializers.CharField(label=_("agent_id"))

class PermissionSerializer(serializers.ModelSerializer):

    class Meta:

        model = UserPermissions
        fields = ['id', 'is_admin', 'is_active', 'creating_access', 'reading_access', 'updating_access', 'deleting_access']

class FilteredListSerializer(serializers.ListSerializer):
    """Filter the list of object in nested serializer according to the connected user_profile"""

    def to_representation(self, data):
        data = data.filter(user_profile=self.context['request'].user)
        return super(FilteredListSerializer, self).to_representation(data)

class FilteredPermissionSerializer(serializers.ModelSerializer):
    """Handle the user_permissions that whill be showed in the agent list -> class AgentManagerSerilaizer / nested"""

    class Meta:
        fields = ['id', 'is_admin', 'is_active', 'creating_access', 'reading_access', 'updating_access', 'deleting_access']

        list_serializer_class = FilteredListSerializer
        model = UserPermissions






class FilteredListSerializer2(serializers.ListSerializer):
    """Filter the list of object in nested serializer according to the connected user_profile"""

    def to_representation(self, data):
        data = data.all()
        return super(FilteredListSerializer2, self).to_representation(data)

class FilteredPermissionSerializer2(serializers.ModelSerializer):
    """Handle the user_permissions that whill be showed in the agent list -> class AgentManagerSerilaizer / nested"""

    class Meta:
        fields = ['id', 'is_admin', 'is_active', 'user_profile']

        list_serializer_class = FilteredListSerializer2
        model = UserPermissions

class GetAgentInfoSerializer(serializers.ModelSerializer):
    """Serialize class for Agent"""
    permission = FilteredPermissionSerializer2(many=True, required=False)
    #owner = serializers.CharField(source=UserPermissions.is_admin)

    class Meta:
        model = Agent
        fields = ['id', 'name', 'language', 'port', 'status', 'permission']



class AgentStatusSerializer(serializers.Serializer):
    """Serialize class for Agent status"""

    status = serializers.CharField(max_length=50)


class FilteredRelatedAgentSerializer(serializers.ListSerializer):
    """Filter the list of related agents, except of the current agent"""

    def to_representation(self, data):

        data = data.all().exclude(id=self.context['agent_id'])
        return super(FilteredRelatedAgentSerializer, self).to_representation(data)

class AgentRelationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ['id', 'language']
        list_serializer_class = FilteredRelatedAgentSerializer

class RelatedAgentSerializer(serializers.ModelSerializer):
    #agents = AgentRelationsSerializer(many=True, required = True)
    agents =  serializers.SerializerMethodField()
    class Meta:
        model = Related_Agent
        fields = ['agents']
        extra_kwargs = {
        'agents': {'read_only': True, 'required': False}}

    def get_agents(self, obj):
        print(self.context['agent_id'])
        return AgentRelationsSerializer(obj.agents.all(), many=True, context={'agent_id': self.context['agent_id']}).data



class AgentManagerSerializer(serializers.ModelSerializer):
    """Serialize class for Agent"""
    permission = FilteredPermissionSerializer(many=True, required=False, read_only=True)
    #related_agent = RelatedAgentSerializer(many=False, required=False, read_only=True, context={'agent_id': id})
    related_agent = serializers.SerializerMethodField()
    class Meta:
        model = Agent
        fields = ['id', 'name', 'language', 'time_zone', 'image', 'date_create', 'port', 'status', 'description', 'related_agent', 'permission']
        extra_kwargs = {
            'permission_serializer': {'read_only': True},
            'date_create': {'read_only': True},
            'date_update': {'read_only': True},
            'port': {'read_only': True},
            'status': {'read_only': False},
            'image': {'required': False},
            'description': {'required': False},
            'related_agent': {'read_only': True, 'required': False},

        }

    def get_related_agent(self, obj):
        return RelatedAgentSerializer(obj.related_agent, many=False,read_only=True,
                                        context={'agent_id': obj.id}).data

    def create(self, validated_data):
        """Create and return a new agent"""

        #print("validated data",validated_data)

        if "path_to_user_folder" in self.context:
            path_to_user_folder = self.context["path_to_user_folder"]

        if validated_data.get('image'):
            agent = Agent.objects.create(
            name = validated_data['name'],
            language = validated_data['language'],
            image = validated_data['image'],
            time_zone = validated_data['time_zone'],
            description = validated_data['description']
            )
        elif validated_data.get("imageName"):

            try:
                image_path = os.path.join(path_to_user_folder, 'images', str(validated_data["imageName"]))
                agent = Agent.objects.create(
                    name=validated_data['name'],
                    language=validated_data['language'],
                    image=File(open(image_path, 'rb')),
                    time_zone=validated_data['time_zone'],
                    description=validated_data['description']
                )

            except:
                raise serializers.ValidationError(
                    {'Erreur': [_("erreur lors de l'importation de l'agent")]})

            try:
                if "intent_set" in validated_data and validated_data.get("intent_set"):
                    for intent in validated_data["intent_set"]:
                        serializer = IntentManagerSerializer(data=intent,
                                                             context={'agentid': agent.id,
                                                                      'path_to_user_folder': path_to_user_folder,
                                                                      'request' : self.context['request']})
                        if serializer.is_valid():
                            serializer.create(intent)
            except:
                Agent.objects.filter(id=agent.id).delete()
                raise serializers.ValidationError({'Erreur': [_("erreur lors de l'importation de l'agent " + str(validated_data["name"]))]})
        else:
            agent = Agent.objects.create(
            name = validated_data['name'],
            language = validated_data['language'],

            time_zone = validated_data['time_zone'],
            description = validated_data['description']
            )

        '''IF the user is admin and the created agent is default
        Once the super user create a default agent this agent will be affected to all the existing users'''
        if "/defaultagent/" in self.context['request'].path and self.context['request'].user.is_superuser:
            agent.is_default = True

            '''affect the created default_agent to all the existing users'''
            users = UserProfile.objects.exclude(id = self.context['request'].user.id)
            for user in users:

                UserPermissions.objects.create(
                    agent=agent,
                    user_profile=user,
                    is_admin=False,
                    creating_access=False,
                    reading_access=True,
                    updating_access=False,
                    deleting_access=False,

                )
        if 'is_default' in validated_data and validated_data['is_default'] and not (self.context['request'].user.is_superuser):
            agent.delete()
            raise serializers.ValidationError({'Erreur': [_("Vous n'avez pas le deroit de créer un agent par defaut")]})

        if not "path_to_user_folder" in self.context:
            related_agent = Related_Agent.objects.create(name = agent.name)
            agent.related_agent = related_agent

        agent.port=agent.pk+8000
        agent.save()

        UserPermissions.objects.create(
            agent=agent,
            user_profile=self.context['request'].user,
            is_admin=True,
            creating_access=True,
            reading_access=True,
            updating_access=True,
            deleting_access=True,

        )
        return agent

    def update(self, instance, validated_data):
        if "path_to_user_folder" in self.context:
            path_to_user_folder = self.context["path_to_user_folder"]

        if 'name' in validated_data and validated_data.get('name'):
            instance.name = validated_data.get('name', instance.name)
        if 'language' in validated_data and validated_data.get('language') and instance.language != validated_data.get('language'):
            exist_language = Agent.objects.filter(related_agent=instance.related_agent).values_list('language', flat=True)
            print("exist_language:   ", exist_language)
            if validated_data.get('language') in exist_language:
                raise serializers.ValidationError({'Erreur': [_("This language is already in use for this agent ")]})
            else:
                instance.language = validated_data.get('language', instance.language)
        if validated_data.get('image'):
            instance.image = validated_data.get('image', instance.image)

        if validated_data.get("imageName"):
            image_path = os.path.join(path_to_user_folder, 'images', str(validated_data["imageName"]))
            instance.image = File(open(image_path, 'rb'))

        if 'time_zone' in validated_data and validated_data.get('time_zone'):
            instance.time_zone = validated_data.get('time_zone', instance.time_zone)

        if not instance.port:
            instance.port = instance.pk+8000

        if 'status' in validated_data and validated_data.get('status'):
            instance.status = validated_data.get('status', instance.status)

        if 'description' in validated_data and validated_data.get('description'):
            instance.description = validated_data.get('description', instance.description)
        instance.save()

        try:
            if "intent_set" in validated_data and validated_data.get("intent_set"):
                for intent in validated_data["intent_set"]:
                    serializer = IntentManagerSerializer(data=intent,
                                                         context={'agentid': instance.id,
                                                                  'path_to_user_folder': path_to_user_folder})
                    if serializer.is_valid():
                        serializer.create(intent)
        except:
            Agent.objects.filter(id=instance.id).delete()
            raise serializers.ValidationError({'Erreur': [_("erreur lors de la restoration de l'agent " + str(validated_data["name"]))]})

        return instance

class UserProfileForUserPermissions(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email']
        extra_kwargs = {
            'first_name': {'read_only': True},
            'last_name': {'read_only': True},
        }

class AgentCustomerManagerSerializer(serializers.ModelSerializer):
    user_profile = EmailField(source='user_profile.email')

    class Meta:
        model = UserPermissions
        fields = ['id', 'agent','is_active','is_admin', 'creating_access', 'reading_access',
                  'updating_access', 'deleting_access', 'user_profile']
        extra_kwargs = {
            'agent': {'read_only': True},
            'is_admin': {'read_only': True},
            'is_active': {'read_only': True},

        }

    def create(self, validated_data):
        """Create and return a new intent"""

        try:
            agent = Agent.objects.get(pk=self.context['agentid'])
        except(TypeError, ValueError, OverflowError, Agent.DoesNotExist):
            raise serializers.ValidationError({'Agentid': [_("Cet agent n'existe pas")]})

        try:
            print(validated_data['user_profile']['email'])
            user = UserProfile.objects.get(email=validated_data['user_profile']['email'])
        except(TypeError, ValueError, OverflowError, UserProfile.DoesNotExist):
            raise serializers.ValidationError({'User': [_("Cet utilisateur n'existe pas")]})

        isExistRelation = UserPermissions.objects.filter(agent=agent, user_profile=user)
        if (len(isExistRelation) !=0):
            raise serializers.ValidationError({'Erreur':
                        [_("Il y'avait deja une relation entre cet utilisateur et cet agent ")]})

        userPermission=UserPermissions.objects.create(
            agent=agent,
            user_profile=user,
            is_admin=False,
            creating_access=validated_data['creating_access'],
            reading_access=validated_data['reading_access'],
            updating_access=validated_data['updating_access'],
            deleting_access=validated_data['deleting_access'],
            is_active=False,
        )

        """Send an email to the specified user with the acceptation link"""
        mail_subject ='You are invited to manage new Agent.'
        current_site = get_current_site(self.context.get('request'))
        userPermissionID = userPermission.id
        encodedUserPermissionID = urlsafe_base64_encode(force_bytes(userPermissionID))
        acceptation_link = "{0}accepteinvit/{1}".format(urlServer, encodedUserPermissionID)

        message = "Hello {0} {1},\n {2} {3} invit you to manage the agent {4}. \n" \
                  "Please follow the link mentioned bellow to Accept/Reject the invitation. \n {5}"\
            .format(user.last_name, user.first_name,
                    self.context['request'].user.last_name, self.context['request'].user.first_name,
                    agent.name, acceptation_link)
        to_email = user.email
        send_mail(
            mail_subject,
            message,
            EMAIL_HOST_USER,
            [to_email],
            fail_silently=False,
        )
        return userPermission

class InvitationManagerSerializer(serializers.Serializer):
    """Serializers a name field for testing our APIView"""

    invitID = serializers.CharField(max_length=50)


class AddQuestionToIntent(serializers.Serializer):
    """Serializers a name field for testing our APIView"""

    question = serializers.CharField(max_length=1500)
    intentID=serializers.IntegerField()
    def validate(self, validated_data, *args, **kwargs):

        print("DATA is showed here", self.context['agentid'])

        try:
            intentObj=Intent.objects.get(id=validated_data['intentID'])
        except:
            raise serializers.ValidationError(
                {'Erreur': [_("Une erreur est parvenue lors de la recuperation de l'intention {}".format(validated_data['intentID']))]})

        if intentObj.agent.id != self.context['agentid']:
            raise serializers.ValidationError(
                {'Erreur': [_("Vous devez specifier des intents appartenants au meme agent specifié")]})

        try:
            question=Question.objects.create(name=validated_data['question'],
                                         intent = intentObj,
                                         order = 1)
        except:
            raise serializers.ValidationError(
                {'Erreur': [_("Vous devez verifier le contenues de questions")]})
        return True