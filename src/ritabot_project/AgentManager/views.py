
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination, BasePagination
from collections import OrderedDict, namedtuple
from AgentManager import serializers, export_serializers
from rest_framework.views import APIView, View
from rest_framework import filters
from rest_framework.exceptions import ValidationError
import time
import requests
from AgentManager.default_entity import defaultEntitys
from AgentManager.specific_intent import Francais, Anglais, TunisienDialecte, Arabe
from ProfileManager.models import *
"""     Response types        """
from rest_framework.response import Response
from django.http import HttpResponse
from django.http import JsonResponse
"""     Permissions and token import modules    """
from rest_framework.authentication import TokenAuthentication
from AgentManager import permissions
from rest_framework.permissions import IsAuthenticated
"""For images and files"""
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser, JSONParser
from .training import *
from .translate_intent import *
from .renderers import ZIPRenderer
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
import os
import shutil
import subprocess
import socket
from contextlib import closing
from ritabot.settings import *
from .models import *
#image decoding
import base64
from django.core.files.base import ContentFile
import zipfile

""" for persistent menu settings with facebook """
from AgentManager import menu_persistent
from AgentManager.facebook_api_calls import PersistentMenu, GetStarted

"""CODING/DECODING"""

from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

""" import crontab """
from crontab import CronTab
import getpass

"""     Const   """
IP_ADDRESS = urlServer
EXPORT_FOLDER = "to_export"
IMPORT_FOLDER = "to_import"

import json
from os.path import dirname


class Service:

    create_url = create_service_url
    update_url = update_service_url

    head = {'Authorization': 'Token {}'.format(str(token_admin_url_dashboard)),
            'Content-Type': 'application/json'}
    def __init__(self):
        pass

    def get_path(self, x, func_name):
        # todo : remove user from pickle file
        abs_path = dirname(dirname(dirname(os.getcwd())))
        relative_path = 'share_services/data.json'
        filename = os.path.join(abs_path, relative_path)
        print("filename :", filename)
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as file:
                    json_data = json.load(file)
                    if str(x) in json_data:
                        if func_name == "get_service_id":
                            return True, json_data[str(x)]["service_id"]
                        elif func_name == "get_instance_id":
                            return True, json_data["instance_id"]
                    else:
                        return False, None
            else:
                return False, None
        except Exception as e:
            print("e :", e)
            return False, None

    def get_instance_id(self):
        state, instance_id = self.get_path("instance_id", "get_instance_id")
        return state, instance_id

    def get_service_id(self, port):
        state, service_id = self.get_path(port, "get_service_id")
        return state, service_id

    def create_service(self, data):
        try:
            state, instance_id = self.get_instance_id()
            if state:
                r = requests.post(Service.create_url.format(str(instance_id)), json=data, timeout=10, headers=Service.head)
                print("status share_instance : ", r.status_code)
                print(r.json())
        except Exception as e:
            print(e)
            pass

    def update_service(self, port, data):
        try:

            state1, instance_id = self.get_instance_id()
            state2, service_id = self.get_service_id(port)
            print(state1, instance_id, state2, service_id)
            if state1 and state2:
                r = requests.put(Service.update_url.format(str(instance_id), str(service_id)), json=data, timeout=10, headers=Service.head)
                print("status update service : ", r.status_code)
                print(r.json())
        except Exception as e:
            print(e)
            pass

    def delete_service(self, port):
        try:
            state1, instance_id = self.get_instance_id()
            state2, service_id = self.get_service_id(port)
            if state1 and state2:
                print("url :", )
                r = requests.delete(Service.update_url.format(str(instance_id), str(service_id)), timeout=10, headers=Service.head)
                print("status delete service : ", r.status_code)
                print(r.json())
        except Exception as e:
            print(e)
            pass

"""     Define the pagination class for agent managment"""
class StandardResultsSetPagination(PageNumberPagination, BasePagination):
    page_size = 1000
    page_query_param="pageindex"
    page_size_query_param = 'pagesize'
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('totalCount', self.page.paginator.count),

            ('agentList', data)
        ]))


"""     Define the pagination class for intent managment"""
class StandardIntentResultsSetPagination(PageNumberPagination, BasePagination,):
    page_size = 1000
    page_query_param="pageindex"
    page_size_query_param = 'pagesize'
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('totalCount', self.page.paginator.count),

            ('intentList', data)
        ]))

"""Agent status class"""
class AgentStatusManager(APIView):

    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.AgentStatusSerializer
    permission_classes = (IsAuthenticated, permissions.AgentStatusPemissions)

    def post(self, request, agentID):
        try:
            agent=Agent.objects.get(id=agentID)
        except:
            return Response({"erreur" : "agent not found"})
        agent.status='entrainer'
        agent.save()

        # todo : update service
        try:
            data = {
                "name": agent.name,
                "port": agent.port,
                "description": agent.description,
                "service_id": agent.id,
                "language": agent.language,
                "training_status": agent.status,
                "service_type": "Chatbot",
                "created_at": str(agent.date_create),
                "updated_at": str(agent.date_update)
            }
            service = Service()
            service.update_service(agent.port, data)
        except:
            pass

        return Response({"success": "ok"})


def StopAgentPort(agent_port, user_id, agent_id):
    cmd = "sudo systemctl stop agent_" + str(agent_port) + ".service; sudo systemctl disable agent_" + str(agent_port) + ".service; sudo rm -r /etc/systemd/system/agent_" + str(agent_port) + ".service ; sudo rm -r /etc/nginx/sites-available/agent_" + str(agent_port) + "; sudo rm -r /etc/nginx/sites-enabled/agent_" + str(agent_port)
    try:
        subprocess.call(cmd, shell=True)
    except:
        pass

    try:
        # get username sytem
        username = getpass.getuser()
        # create crontab_instance
        my_cron = CronTab(user=username)
        # Clearing Jobs that its clear_context name From Crontab
        for job in my_cron:
            if job.comment in ('Crontab_clear_context_' + str(user_id) + '_' + str(agent_id), 'Crontab_agent_' + str(agent_port) ):
                my_cron.remove(job)
                my_cron.write()
    except:
        pass

"""Agent managment class"""
class AgentManager(viewsets.ModelViewSet):

    parser_classes = (MultiPartParser, FormParser)
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.AgentManagerSerializer
    queryset = Agent.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAuthenticated, permissions.AgentPermissions)
    #permission_classes = (IsAuthenticated, permissions.AgentPermissions)

    def create(self, request, *args, **kwargs):

        req=None
        if request.data['image'] and type(request.data['image'])==str:
            format, imgstr = request.data['image'].split(';base64,')
            ext = format.split('/')[-1]
            print('####image', request.data['image'])
            print("extension",ext)
            print("request.data",request.data)
            imagefield= ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            req=request.data.copy()
            req['image']=imagefield

        if req:
            serializer = serializers.AgentManagerSerializer(data=req, context={'request': self.request})
        else:
            serializer = serializers.AgentManagerSerializer(data=request.data, context={'request': self.request})

        if serializer.is_valid():
            agent = serializer.save()
            # self.context['agentid'] = agent.id
            if "/agent/" in self.request.path:
                if agent.language == "Francais":
                    langue=Francais()

                elif agent.language == "Dialecte tunisien":
                    langue = TunisienDialecte()
                elif agent.language == "Arabe":
                    langue = Arabe()
                #elif agent.language == "Anglais":
                else:
                    langue = Anglais()

                serializer = serializers.IntentManagerSerializer(data=langue.getdepart(), context={'request': self.request, 'agentid': agent.id})
                if serializer.is_valid():

                    intentObj = serializer.save()
                    intentObj.is_depart=True
                    intentObj.save()

                serializer = serializers.IntentManagerSerializer(data=langue.getdepartfacebook(),
                                                                 context={'request': self.request, 'agentid': agent.id})
                if serializer.is_valid():
                    intentObj = serializer.save()
                    intentObj.is_depart = True
                    intentObj.save()

                serializer = serializers.IntentManagerSerializer(data=langue.getnoresponse(), context={'request': self.request, 'agentid': agent.id})
                if serializer.is_valid():
                    intentObj = serializer.save()
                    intentObj.is_none_response = True
                    intentObj.save()

                serializer = serializers.IntentManagerSerializer(data=langue.getdisabled(), context={'request': self.request, 'agentid': agent.id})
                if serializer.is_valid():
                    intentObj = serializer.save()
                    intentObj.is_active = False
                    intentObj.save()
                entities = defaultEntitys.GetEntitys(self)
                for entity in entities:
                    serializer = serializers.EntityManagerSerializer(data=entity,
                                                                     context={'request': self.request,
                                                                              'agentid': agent.id})
                    if serializer.is_valid():
                        entityObj = serializer.save()
                        entityObj.is_default = True
                        entityObj.save()


                # todo : create service
                try:
                    permissions_list = UserPermissions.objects.filter(agent=agent)
                    if permissions_list:
                        users = [perm.user_profile.email for perm in permissions_list]
                    data = {
                        "name": agent.name,
                        "port": agent.port,
                        "description": agent.description,
                        "service_id": agent.id,
                        "language": agent.language,
                        "training_status": agent.status,
                        "service_type": "Chatbot",
                        "created_at": str(agent.date_create),
                        "updated_at": str(agent.date_update),
                        "payload": {
                            "time_zone": str(agent.time_zone),
                            "related_agent": str(agent.related_agent.id),
                            "users": users,
                        }
                    }
                    service = Service()
                    service.create_service(data)
                except:
                    pass

            return Response({"success": True})
        return Response({"success": False})

    def update(self, request, *args, **kwargs):
        serializer = serializers.AgentManagerSerializer(data=request.data, context={'request': self.request})
        if serializer.is_valid():
            instance = self.get_object()
            agent = serializer.update(instance, self.request.data)
            # todo : update service
            try:
                data = {
                    "name": agent.name,
                    "port": agent.port,
                    "description": agent.description,
                    "service_id": agent.id,
                    "language": agent.language,
                    "training_status": agent.status,
                    "service_type": "Chatbot",
                    "created_at": str(agent.date_create),
                    "updated_at": str(agent.date_update)
                }
                service = Service()
                service.update_service(agent.port, data)
            except:
                pass
            return Response({"success": True})
        return Response({"success": False})

    def get_queryset(self):
        if "/agent/" in self.request.path:
            perm= UserPermissions.objects.filter(user_profile=self.request.user, is_active=True).values('agent')
            agent= Agent.objects.filter(id__in =perm, is_default=False, is_main=True)
            return (agent)
        elif "/defaultagent/" in self.request.path:
            perm = UserPermissions.objects.filter(user_profile=self.request.user, is_active=True).values('agent')
            if self.request.user.is_superuser:
                agent = Agent.objects.filter(id__in=perm, is_default=True)
            else:
                agent = []
            return (agent)

    def destroy(self, request, *args, **kwargs):
        related_agent = self.get_object().related_agent.agents.all()
        for agent in related_agent:
            instanceId = agent.id
            intent_set = agent.intent_set.all()

            for intent in intent_set:
                try:
                    mixed_response_set = intent.block_response_set.all()[0].mixed_response_set.all()
                    for instance in mixed_response_set:
                        try:
                            x = [os.remove(images.image.path) for images in instance.image_set.all()]
                        except:
                            pass
                        try:
                            y = [os.remove(imageslider.image.path) for slider in instance.gallery_set.all() for imageslider in
                                 slider.slider_set.all()]
                        except:
                            pass
                except:
                    pass

                try:
                    related_videos = intent.related_videos.all()
                    z = [os.remove(video.video.video.path) for video in related_videos]
                except:
                    pass
                try:
                    p = [video.video.delete() for video in related_videos]
                except:
                    pass
                try:
                    related_audios = intent.related_audios.all()
                    w = [os.remove(audio.audio.audio.path) and audio.audio.delete() for audio in related_audios]
                except:
                    pass
                try:
                    p = [audio.audio.delete() for audio in related_audios]
                except:
                    pass
            """Delete the generated data"""
            try:
                shutil.rmtree(os.path.join("AI", "data", "folder_user_{}".format(request.user.id),
                                           "agent_{}".format(instanceId)))
            except:
                pass
            try:
                shutil.rmtree(os.path.join("to_export"))
            except:
                pass
            try:
                shutil.rmtree(os.path.join("to_import"))
            except:
                pass
            try:
                shutil.rmtree(os.path.join("AI", "data_corrector", "folder_user_{}".format(request.user.id),
                                           "agent_{}".format(instanceId)))
            except:
                pass

            try:
                shutil.rmtree(os.path.join("AI", "data_trainer_output", "folder_user_{}".format(request.user.id),
                                           "agent_{}".format(instanceId)))
            except:
                pass

            StopAgentPort(agent.port, self.request.user.id, instanceId)
            #todo delete service
            try:
                service = Service()
                service.delete_service(agent.port)
            except:
                pass
            Agent.objects.filter(id=instanceId).delete()
        return Response({"success": True})


"""launch training class"""
class AgentLanguageManager(APIView):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    #TODO: Add permission class for launch training class

    def post(self, request,agentid):
        language = request.data['language']
        agent_id = agentid
        try:
            main_agent = Agent.objects.get(id=agent_id)
        except(TypeError, ValueError, OverflowError, Agent.DoesNotExist):
            return Response({"error":"This agent does not exist"})
        exist_language = Agent.objects.filter(related_agent = main_agent.related_agent).values_list('language', flat=True)
        print("exist_language:   ", exist_language)
        if language in exist_language:
            return Response({"error": "This language is already in use for this agent"})
        agent = Agent.objects.create(
            name=main_agent.name + "_"+language,
            language=language,
            time_zone=main_agent.time_zone,
            description=main_agent.description,
            related_agent = main_agent.related_agent,
            is_main = False
        )
        agent.port = agent.pk + 8000
        agent.save()
        UserPermissions.objects.create(
            agent=agent,
            user_profile=self.request.user,
            is_admin=True,
            creating_access=True,
            reading_access=True,
            updating_access=True,
            deleting_access=True,

        )


        if agent.language == "Francais":
            langue = Francais()

        elif agent.language == "Dialecte tunisien":
            langue = TunisienDialecte()
        elif agent.language == "Arabe":
            langue = Arabe()
        # elif agent.language == "Anglais":
        else:
            langue = Anglais()

        serializer = serializers.IntentManagerSerializer(data=langue.getdepart(),
                                                         context={'request': self.request, 'agentid': agent.id})
        if serializer.is_valid():
            intentObj = serializer.save()
            intentObj.is_depart = True
            intentObj.save()

        serializer = serializers.IntentManagerSerializer(data=langue.getdepartfacebook(),
                                                         context={'request': self.request, 'agentid': agent.id})
        if serializer.is_valid():
            intentObj = serializer.save()
            intentObj.is_depart = True
            intentObj.save()

        serializer = serializers.IntentManagerSerializer(data=langue.getnoresponse(),
                                                         context={'request': self.request, 'agentid': agent.id})
        if serializer.is_valid():
            intentObj = serializer.save()
            intentObj.is_none_response = True
            intentObj.save()

        serializer = serializers.IntentManagerSerializer(data=langue.getdisabled(),
                                                         context={'request': self.request, 'agentid': agent.id})
        if serializer.is_valid():
            intentObj = serializer.save()
            intentObj.is_active = False
            intentObj.save()
        entities = defaultEntitys.GetEntitys(self)
        for entity in entities:
            serializer = serializers.EntityManagerSerializer(data=entity,
                                                             context={'request': self.request,
                                                                      'agentid': agent.id})
            if serializer.is_valid():
                entityObj = serializer.save()
                entityObj.is_default = True
                entityObj.save()

        intent_list = Intent.objects.filter(agent = main_agent, is_active=True, is_depart=False, is_none_response=False).values_list('id', flat=True)
        for intent in intent_list:
            print("traduire l'intent_id {0} de l'agent {1} vers l'agent {2} language source {3}, language desirée{4}".format(intent,agent_id, agent.id, language, main_agent.language))
            translate(agent.id, intent, main_agent.language, self.request)


        # todo : create service
        try:
            data = {
                "name": agent.name,
                "port": agent.port,
                "description": agent.description,
                "service_id": agent.id,
                "language": agent.language,
                "training_status": agent.status,
                "service_type": "Chatbot",
                "created_at": str(agent.date_create),
                "updated_at": str(agent.date_update)
            }
            service = Service()
            service.create_service(data)
        except:
            pass


        return Response({"success":"ok"})

"""Delete Language"""
class Delete_Language(APIView):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,permissions.IntentPermissions)

    def post(self, request, agentid):
        agent_id = request.data['agent_id']
        try:
            agent = Agent.objects.get(id=agent_id, is_main=False)
            main_agent = Agent.objects.get(id=agentid, is_main=True)
        except(TypeError, ValueError, OverflowError, Agent.DoesNotExist):
            return Response({"error":"This language does not exist"})
        if main_agent.related_agent == agent.related_agent:
            pass
        else:
            return Response({"error": "The language should be refered to a valid agent"})
        json_response = dict()
        json_response["success"] = "ok"

        instanceId = agent.id
        agent_port = agent.port
        intent_set = agent.intent_set.all()

        for intent in intent_set:
            try:
                mixed_response_set = intent.block_response_set.all()[0].mixed_response_set.all()
                for instance in mixed_response_set:
                    try:
                        x = [os.remove(images.image.path) for images in instance.image_set.all()]
                    except:
                        pass
                    try:
                        y = [os.remove(imageslider.image.path) for slider in instance.gallery_set.all() for imageslider
                             in
                             slider.slider_set.all()]
                    except:
                        pass
            except:
                pass

            try:
                related_videos = intent.related_videos.all()
                z = [os.remove(video.video.video.path) for video in related_videos]
            except:
                pass
            try:
                p = [video.video.delete() for video in related_videos]
            except:
                pass
            try:
                related_audios = intent.related_audios.all()
                w = [os.remove(audio.audio.audio.path) and audio.audio.delete() for audio in related_audios]
            except:
                pass
            try:
                p = [audio.audio.delete() for audio in related_audios]
            except:
                pass
        """Delete the generated data"""
        try:
            shutil.rmtree(os.path.join("AI", "data", "folder_user_{}".format(request.user.id),
                                       "agent_{}".format(instanceId)))
        except:
            pass
        try:
            shutil.rmtree(os.path.join("to_export"))
        except:
            pass
        try:
            shutil.rmtree(os.path.join("to_import"))
        except:
            pass
        Agent.objects.filter(id=instanceId).delete()

        # todo delete service
        try:
            service = Service()
            service.delete_service(agent_port)
        except:
            pass
        return Response(json_response)




"""launch training class"""
class LaunchTraining(APIView):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,permissions.TrainngManagePermissions)

    def post(self, request):
        print(request.data)  # will receive agent_id
        agent_id = request.data['agent_id']
        try:
            main_agent = Agent.objects.get(id=agent_id)
        except(TypeError, ValueError, OverflowError, Agent.DoesNotExist):
            return Response({"error":"This agent does not exist"})
        json_response = dict()
        json_response["success"] = "ok"
        user_id = request.user.id
        related_agent = main_agent.related_agent.agents.all()
        for agent in related_agent:
            print("launch training of agent: ", agent.name)
            json_file = generate_json(user_id, agent.id)
            if os.path.exists(json_file):
                if agent.language == 'Francais':
                    lang='french'
                if agent.language == 'Anglais':
                    lang = 'english'
                if agent.language == 'Dialecte tunisien':
                    lang = 'tunisian'
                if agent.language == 'Arabe':
                    lang = 'arabic'
                agent.status = "in_training"
                agent.save()

                # todo : update service
                try:
                    data = {
                        "name": agent.name,
                        "port": agent.port,
                        "description": agent.description,
                        "service_id": agent.id,
                        "language": agent.language,
                        "training_status": agent.status,
                        "service_type": "Chatbot",
                        "created_at": str(agent.date_create),
                        "updated_at": str(agent.date_update)
                    }
                    service = Service()
                    service.update_service(agent.port, data)
                except:
                    pass

                cmd = "python3" + " " + training_path + "main_trainer.py" + " " + str(lang) + " " + str(user_id) + " " + str(agent.id)
                subprocess.Popen(cmd.split())
            else:
                return Response(json_file)
        return Response(json_response)

class Stop_Agent(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,permissions.Stop_Agent_Permission)

    def check_socket(self, host, port):
        """ Check if the related port is already in use or not"""

        ipwith = host.split('//')[-1]
        ip = ipwith.split('/')[0]

        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:

            if sock.connect_ex((ip, port)) == 0:  # port not available
                return False
            else:
                return True

    def post(self, request):
        agent_id = request.data['agent_id']
        try:
            main_agent = Agent.objects.get(id=agent_id)
        except:
            return Response({"erreur": "Agent invalide"})
        related_agent = main_agent.related_agent.agents.all()
        for agent in related_agent:
            verif = self.check_socket(IP_ADDRESS, agent.port)
            if not verif:
                cmd = "sudo systemctl stop agent_" + str(agent.port) + ".service; sudo systemctl disable agent_" + str(agent.port) + ".service"
                subprocess.call(cmd, shell=True)
                try:
                    # get username sytem
                    username = getpass.getuser()
                    # create crontab_instance
                    my_cron = CronTab(user=username)
                    # Clearing Jobs that its clear_context name From Crontab
                    for job in my_cron:
                        if job.comment == 'Crontab_agent_' + str(agent.port):
                            my_cron.remove(job)
                            my_cron.write()
                except:
                    pass
                # subprocess.call("sudo fuser -k -n tcp " + str(agent.port), shell=True)
                agent.status ='entrainer'
                agent.save()

                # todo : update service
                try:
                    data = {
                        "name": agent.name,
                        "port": agent.port,
                        "description": agent.description,
                        "service_id": agent.id,
                        "language": agent.language,
                        "training_status": agent.status,
                        "service_type": "Chatbot",
                        "created_at": str(agent.date_create),
                        "updated_at": str(agent.date_update)
                    }
                    service = Service()
                    service.update_service(agent.port, data)
                except:
                    pass
            # else:
            #     return Response({"erreur": "Cet agent n'été pas en cours d'execution"})
            else:
                agent.status = 'entrainer'
                agent.save()

                # todo : update service
                try:
                    data = {
                        "name": agent.name,
                        "port": agent.port,
                        "description": agent.description,
                        "service_id": agent.id,
                        "language": agent.language,
                        "training_status": agent.status,
                        "service_type": "Chatbot",
                        "created_at": str(agent.date_create),
                        "updated_at": str(agent.date_update)
                    }
                    service = Service()
                    service.update_service(agent.port, data)
                except:
                    pass
        return Response({"success": "ok"})




"""Test training class"""
class TestTraining(APIView):
    """
    Test training of a specific agent
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,permissions.TrainngManagePermissions)

    # TODO: Add permission class for launch training class
    #TODO: Not yet Tested
    def check_socket(self, host, port):
        ipwith=host.split('https://')[-1]
        ip=ipwith.split('/')[0]

        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:

            if sock.connect_ex((ip, port)) == 0:  # port not available
                return False
            else:
                return True

    def post(self, request):
        print(request.data)  # will receive agent_id
        agent_id = request.data['agent_id']
        #TODO: add exception handling
        main_agent = Agent.objects.get(id=agent_id)
        user = request.user
        json_response = dict()
        json_response["success"] = "ok"
        user_id = request.user.id
        related_agent = main_agent.related_agent.agents.all()
        for agent in related_agent:
            if agent.language == 'Francais':
                lang = 'french'
            if agent.language == 'Anglais':
                lang = 'english'
            if agent.language == 'Dialecte tunisien':
                lang = 'tunisian'
            if agent.language == 'Arabe':
                lang = 'arabic'
            # cmd = 'sudo nohup gunicorn --name="'+ str(lang) + " "+ str(user_id) + " "+str(agent.id) + '"'+ "" \
            # " --bind 0.0.0.0:" +str(agent.port)+ " wsgi --certfile=/etc/nginx/ssl/domain.crt " \
            # "--keyfile=/etc/nginx/ssl/domain.key" + " --chdir "+training_path + " --threads 100" + " "+ " &"
            cmd_test = "sudo systemctl daemon-reload; sudo systemctl start agent_" + str(agent.port) + ".service; sudo systemctl enable agent_" + str(agent.port) + ".service"
            x = self.check_socket(IP_ADDRESS, agent.port)
            if x is False:
                # subprocess.call("sudo fuser -k -n tcp " + str(agent.port) , shell=True)

                cmd_stop = "sudo systemctl stop agent_" + str(agent.port) + ".service; sudo systemctl disable agent_" + str(agent.port) + ".service"
                subprocess.call(cmd_stop, shell=True)
                try:
                    # get username sytem
                    username = getpass.getuser()
                    # create crontab_instance
                    my_cron = CronTab(user=username)
                    # Clearing Jobs that its clear_context name From Crontab
                    for job in my_cron:
                        if job.comment == 'Crontab_agent_' + str(agent.port):
                            my_cron.remove(job)
                            my_cron.write()
                except:
                    pass

            """
            Check Changing the agent status to En marche
            """
            os.system("{}".format(cmd_test))
            try:
                req = requests.get(url='https://dev.ritabot.io:{}/reply/100&0&web&salem'.format(agent.port),
                                   params=None, timeout=300)
            except:
                pass
            agent.status = "En marche"
            agent.save()

            # todo : update service
            try:
                data = {
                    "name": agent.name,
                    "port": agent.port,
                    "description": agent.description,
                    "service_id": agent.id,
                    "language": agent.language,
                    "training_status": agent.status,
                    "service_type": "Chatbot",
                    "created_at": str(agent.date_create),
                    "updated_at": str(agent.date_update)
                }
                service = Service()
                service.update_service(agent.port, data)
            except:
                pass

        return Response(json_response)

"""Output context view"""
class OutputContextManagerView(viewsets.ModelViewSet):
    """Handle reading the output context"""

    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.OutputContextSerializer
    permission_classes = (IsAuthenticated,permissions.outContextpermissions)

    def get_queryset(self):
        perm= UserPermissions.objects.filter(user_profile=self.request.user, is_active=True).values('agent')
        agentid= self.kwargs['agentid']
        excludedIntentID= self.kwargs['intentid']
        agent= Agent.objects.filter(id__in =perm, id=agentid).values('pk')
        intent= Intent.objects.filter(agent__in =agent)
        excludedIntent = Intent.objects.filter(id=excludedIntentID)
        outputContext = OutputContext.objects.filter(intent__in=intent).exclude(intent__in=excludedIntent)
        return (outputContext)

"""Intent manager class"""
class IntentManagerView(viewsets.ModelViewSet):
    """Handle creating reading and updating intents"""

    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.IntentManagerSerializer
    permission_classes = (IsAuthenticated,permissions.IntentPermissions)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    pagination_class = StandardIntentResultsSetPagination
    #TODO: add pagination like agent
    def create(self, request, *args, **kwargs):

        #print(self.request.data)
        verif={"success":True}
        serializer = serializers.IntentManagerSerializer(data=self.request.data, context={'request': self.request, 'agentid': self.kwargs['agentid']})
        if serializer.is_valid():
            serializer.create(self.request.data)
            return Response({"sucess":"ok"})
        raise ValidationError(serializer.error_messages)

    def update(self, request, *args, **kwargs):
        serializer = serializers.IntentManagerSerializer(data=self.request.data, context={'request': self.request, 'agentid': self.kwargs['agentid']})
        if serializer.is_valid():
            instance = self.get_object()
            serializer.update(instance, self.request.data)
            return Response({"sucess":"ok"})
        raise ValidationError(serializer.error_messages)

    def destroy(self, request, *args, **kwargs):
        instanceid = self.get_object().id
        intent=self.get_object()
        if intent.is_depart == True or intent.is_none_response == True:
            raise Exception("Vous ne devez pas supprimer une intention de depart de discution ou de message d'erreur")

        try:
            mixed_response_set = intent.block_response_set.all()[0].mixed_response_set.all()
            for instance in mixed_response_set:
                try:
                    x=[os.remove(images.image.path) for images in instance.image_set.all() ]
                except:
                    pass
                try:
                    y=[os.remove(imageslider.image.path) for slider in instance.gallery_set.all() for imageslider in slider.slider_set.all()]
                except:
                    pass
        except:
            pass
        try:
            related_videos= intent.related_videos.all()
            z=[os.remove(video.video.video.path)  for video in related_videos]
        except:
            pass
        try:
            p=[video.video.delete()  for video in related_videos]
        except:
            pass
        try:
            related_audios= intent.related_audios.all()
            w=[os.remove(audio.audio.audio.path) and audio.audio.delete() for audio in related_audios]
        except:
            pass
        try:
            p=[audio.audio.delete()  for audio in related_audios]
        except:
            pass

        Intent.objects.filter(id=instanceid).delete()
        agentID = self.kwargs['agentid']
        agent = Agent.objects.get(id= agentID)
        agent.status = "non entrainer"
        agent.save()
        return Response({"sucess":"ok"})

    def get_queryset(self):
        perm= UserPermissions.objects.filter(user_profile=self.request.user, is_active=True).values('agent')
        agentid= self.kwargs['agentid']
        agent= Agent.objects.filter(id__in =perm, id=agentid).values('pk')
        intent= Intent.objects.filter(agent__in =agent, is_active=True)
        return (intent)

"""Add default intent manager class"""
class AddDefaultIntentManagerView(viewsets.ModelViewSet):
    """Handle creating default intents"""

    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.AddDefaultIntentManagerSerializer
    permission_classes = (IsAuthenticated,permissions.AddDefaultIntentManagerPermission)

    def create(self, request, *args, **kwargs):

        print(self.request.data)
        verif={"success":True}
        serializer = serializers.AddDefaultIntentManagerSerializer( data=self.request.data, context={'request': self.request, 'agentid': self.kwargs['agentid']})
        if serializer.is_valid():
            serializer.create(self.request.data)
            return Response({"sucess":"ok"})
        raise ValidationError(serializer.error_messages)

    def get_queryset(self):

        return ([])

"""Default Intents manager class"""
class DefaultIntentManagerView(viewsets.ModelViewSet):
    """Handle creating reading and updating intents"""

    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.IntentManagerSerializer
    permission_classes = (IsAuthenticated,permissions.DefaultIntentsPermissions)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    pagination_class = StandardIntentResultsSetPagination


    def get_queryset(self):
        #perm= UserPermissions.objects.filter(user_profile=self.request.user, is_active=True).values('agent')

        if 'tunisien' in self.kwargs['agentName']:
            agentName = 'Dialecte tunisien'
        else:
            agentName = self.kwargs['agentName']
        agent= Agent.objects.filter(name=agentName, is_default=True).values('pk')
        intent= Intent.objects.filter(agent__in=agent)
        return (intent)

class AgentCustomerManager(viewsets.ModelViewSet):
    """Handle the customer of the specifyed agent"""

    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.AgentCustomerManagerSerializer
    queryset = UserPermissions.objects.all()
    permission_classes = (IsAuthenticated,permissions.UserManagePermissions)

    def perform_create(self, serializer):
        serializer = serializers.AgentCustomerManagerSerializer(data=self.request.data, context={'request': self.request, 'agentid': self.kwargs['agentid']})
        if serializer.is_valid():
            userPermissions = serializer.save(is_active=False)
            return Response(serializer.data)

        raise ValidationError(serializer.error_messages)

    def get_queryset(self):
        try:
            perm= UserPermissions.objects.get(user_profile=self.request.user, agent=self.kwargs['agentid'])
        except(TypeError, ValueError, OverflowError, UserPermissions.DoesNotExist):
            raise Exception("Access denied")
        return UserPermissions.objects.filter(agent=self.kwargs['agentid'])

class InvitationManager(APIView):
    #serializer_class = serializers.InvitationManagerSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, invitID):

        decodedinvitID = force_text(urlsafe_base64_decode(invitID))
        try:
            userPermission = UserPermissions.objects.get(pk =decodedinvitID, user_profile=request.user.id)
        except(TypeError, ValueError, OverflowError, UserPermissions.DoesNotExist):
            return Response({'Invitation': 'Invalid action'})

        userPermission.is_active=True
        userPermission.save()
        return Response({'Invitation': 'Invitation successfully accepted'})

    def delete(self, request, invitID):

        decodedinvitID = force_text(urlsafe_base64_decode(invitID))
        try:
            UserPermissions.objects.get(pk =decodedinvitID, user_profile=request.user.id).delete()
        except(TypeError, ValueError, OverflowError, UserPermissions.DoesNotExist):
            return Response({'Invitation': 'Invalid action'})

        return Response({'Invitation': 'Invitation successfully deleted'})


""" Export / Import / Restore with Serializer """


class ExportIntentManager(APIView):
    """
    export_intents(intent_ids, path_to_user_folder)
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, permissions.ExportIntentPermissions)
    renderer_classes = [ZIPRenderer, JSONRenderer, BrowsableAPIRenderer]
    serializer_class = export_serializers.IntentManagerSerializer

    def post(self, request, *args, **kwargs):
        """
        {"list_ids":[intentID,...]}
        """

        try:
            list_ids = request.data["intents_list"]
        except:
            return JsonResponse({"error": "Expected intents_list."})

        if type(list_ids) != list:
            return JsonResponse({"error": "Input expected to be list."})

        if len(list_ids) > 0:

            # 0) check if intent ids exist
            # 1) check agent permissions
            permissions = UserPermissions.objects.filter(user_profile=self.request.user, is_active=True).values('agent')
            agents = Agent.objects.filter(id__in=permissions)
            intents = Intent.objects.filter(agent__in=agents).order_by('-date_update').reverse()
            intent_ids = [intent.id for intent in intents]
            for intent_id in list_ids:
                try:
                    Intent.objects.get(id=intent_id)
                except Intent.DoesNotExist:
                    return JsonResponse({"error": "Intent with id " + str(intent_id) + " does not exist."})
                if not intent_id in intent_ids:
                    return JsonResponse({"error": "Vous n'avez pas les permissions requises pour pouvoir exporter le (ou les) intents demandé(s)"})

            # 1) empty working directory to receive new exported data:
            path_to_user_folder = os.path.join(EXPORT_FOLDER, 'user_{}').format(request.user.id)

            if not os.path.exists(path_to_user_folder):
                os.makedirs(path_to_user_folder)
            else:
                shutil.rmtree(path_to_user_folder)
                os.makedirs(path_to_user_folder)

            path = os.path.join(path_to_user_folder, "intents.json")

            # 3) export intents
            queryset = Intent.objects.filter(id__in=list_ids).order_by('-date_update').reverse()
            serializer = self.serializer_class(queryset, many=True)
            with open(path, 'w') as intents_file:
                json.dump({"Intents": serializer.data}, intents_file, ensure_ascii=False, indent=4)

            # 4) collect images related to intent

            images_path = os.path.join(path_to_user_folder, 'images')
            # create images folder if it does not exist
            if not os.path.exists(images_path):
                os.makedirs(images_path)

            block_responses = BlockResponse.objects.filter(intent__in=queryset, is_complex=True)
            print("block responses :", block_responses)
            if len(block_responses) > 0:
                print("yes got block responses")
                mixed_responses = MixedResponse.objects.filter(block_response__in=block_responses)
                print("mixed responses :", mixed_responses)
                images_set = Image.objects.filter(mixed_response__in=mixed_responses)
                print("image set :", images_set)
                if len(images_set) > 0:
                    for image in images_set:
                        try:
                            image_name = os.path.join(images_path, '{}').format(image.imagename())
                            with open(image_name, 'wb') as actual_file:
                                actual_file.write(image.image.read())
                        except:
                            pass
                """ filtering sliders image """
                gallery_set = Gallery.objects.filter(mixed_response__in=mixed_responses)
                if len(gallery_set) > 0:
                    slider_set = Slider.objects.filter(gallery__in=gallery_set)
                    if len(slider_set) > 0:
                        for slider in slider_set:
                            try:
                                image_name = os.path.join(images_path, '{}').format(slider.imagename())
                                with open(image_name, 'wb') as actual_file:
                                    actual_file.write(slider.image.read())
                            except:
                                pass

            # 3) generate zip_file:
            try:
                shutil.rmtree(os.path.join(EXPORT_FOLDER, 'user_exported_{}').format(request.user.id))
            except:
                pass
            shutil.make_archive(
                os.path.join(EXPORT_FOLDER, 'user_exported_{}', 'compressed_{}').format(request.user.id,
                                                                                        request.user.id),
                'zip',
                os.path.join(EXPORT_FOLDER, 'user_{}').format(request.user.id)
            )
            zip_file = open(
                os.path.join(EXPORT_FOLDER, 'user_exported_{}', 'compressed_{}.zip').format(request.user.id,
                                                                                            request.user.id), 'rb')
            response = HttpResponse(zip_file, content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename=name.zip'

            return response
        else:
            return JsonResponse({"intents": "No intent to export."})


class ImportIntentManager(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, permissions.IntentPermissions)
    serializer_class = serializers.IntentManagerSerializer

    def post(self, request, *args, **kwargs):
        """
        {"zip_file":file}
        """
        user_id = request.user.id
        agent_id = self.kwargs['agentid']
        try:
            Agent.objects.get(id=agent_id)
        except Agent.DoesNotExist:
            return JsonResponse({"error": "agent not found."})
        # 1) read zip file and extract its content:
        try:
            zip_file = request.FILES["zip_file"]
        except:
            return JsonResponse({"error": "Expected zip_file."})
        path_to_user_folder = os.path.join(IMPORT_FOLDER, 'user_{}').format(user_id)
        try:
            shutil.rmtree(path_to_user_folder)
        except:
            os.makedirs(path_to_user_folder)

        # 2) extract zip file and import data to database
        zip_ref = zipfile.ZipFile(zip_file, 'r')
        zip_ref.extractall(path_to_user_folder)
        zip_ref.close()

        """ load intents.json file """
        try:
            intents_file = open(os.path.join(path_to_user_folder, 'intents.json'))
        except:
            return JsonResponse({"erreur": "Fichier intents.json non trouvé."})

        try:
            intents = json.load(intents_file)["Intents"]
        except:
            return JsonResponse({"erreur": "Fichier intents.json ne peut pas etre chargé correctement."})

        for intent in intents:
            serializer = serializers.IntentManagerSerializer(data=intent,
                                                             context={'request': self.request,
                                                                      'agentid': self.kwargs['agentid'],
                                                                      'path_to_user_folder': path_to_user_folder})
            if serializer.is_valid():
                serializer.create(intent)
            else:
                raise ValidationError(serializer.error_messages)

        return JsonResponse({"success": "OK"})


class ExportAgentsManager(APIView):
    # renderer_classes = [ZIPRenderer, JSONRenderer, BrowsableAPIRenderer]
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    serializer_class = export_serializers.AgentManagerSerializer
    renderer_classes = [ZIPRenderer, JSONRenderer, BrowsableAPIRenderer]


    #TODO: Add permission class for agent export class

    def post(self, request):
        """
        {"agents_list":[agentID,...]}
        cant export one or many agents

        """
        print(request.data)
        try:
            list_ids = request.data["agents_list"]
        except:
            return JsonResponse({"error": "Expected agents_list."})

        if type(list_ids) != list:
            return JsonResponse({"error": "Input expected to be list."})

        if len(list_ids) > 0:
            # 0) check if agent ids exist
            # 1) check agent permissions
            permissions = UserPermissions.objects.filter(user_profile=self.request.user, is_active=True).values('agent')
            agents = Agent.objects.filter(id__in=permissions)
            agents_ids = [agent.id for agent in agents]
            for agent_id in list_ids:
                try:
                    Agent.objects.get(id=agent_id)
                except Agent.DoesNotExist:
                    return JsonResponse({"error": "Agent with id " + str(agent_id) + " does not exist."})

                if not agent_id in agents_ids:
                    return JsonResponse({"error": "Vous n'avez pas les permissions pour exporter le (ou les) agents demandé(s)"})

            # 1) empty working directory to receive new exported data:
            path_to_user_folder = os.path.join(EXPORT_FOLDER, 'user_{}').format(request.user.id)

            if not os.path.exists(path_to_user_folder):
                os.makedirs(path_to_user_folder)
            else:
                shutil.rmtree(path_to_user_folder)
                os.makedirs(path_to_user_folder)

            path = os.path.join(path_to_user_folder, "agents.json")

            # 2) export agents
            queryset = Agent.objects.filter(id__in=list_ids)
            serializer = self.serializer_class(queryset, many=True)
            with open(path, 'w') as agents_file:
                json.dump({"Agents": serializer.data}, agents_file, ensure_ascii=False, indent=4)


            # 4) collect images related to agents

            images_path = os.path.join(path_to_user_folder, 'images')
            # create images folder if it does not exist
            if not os.path.exists(images_path):
                os.makedirs(images_path)
            else:
                shutil.rmtree(images_path)
                os.makedirs(images_path)

            for agent in queryset:
                try:
                    image_name = os.path.join(images_path, '{}').format(agent.imagename())
                    with open(image_name, 'wb') as actual_file:
                        actual_file.write(agent.image.read())
                except:
                    pass

            # get intent ids
            intents_list = Intent.objects.filter(agent__in=queryset)
            block_responses = BlockResponse.objects.filter(intent__in=intents_list, is_complex=True)
            if len(block_responses) > 0:
                mixed_responses = MixedResponse.objects.filter(block_response__in=block_responses)
                images_set = Image.objects.filter(mixed_response__in=mixed_responses)
                if len(images_set) > 0:
                    for image in images_set:
                        try:
                            image_name = os.path.join(images_path, '{}').format(image.imagename())
                            with open(image_name, 'wb') as actual_file:
                                actual_file.write(image.image.read())
                        except:
                            pass
                """ filtering sliders image """
                gallery_set = Gallery.objects.filter(mixed_response__in=mixed_responses)
                if len(gallery_set) > 0:
                    slider_set = Slider.objects.filter(gallery__in=gallery_set)
                    if len(slider_set) > 0:
                        for slider in slider_set:
                            try:
                                image_name = os.path.join(images_path, '{}').format(slider.imagename())
                                with open(image_name, 'wb') as actual_file:
                                    actual_file.write(slider.image.read())
                            except:
                                pass
            # 3) generate zip_file:
            try:
                shutil.rmtree(os.path.join(EXPORT_FOLDER, 'user_exported_{}').format(request.user.id))
            except:
                pass
            shutil.make_archive(
                os.path.join(EXPORT_FOLDER, 'user_exported_{}', 'compressed_{}').format(request.user.id,
                                                                                        request.user.id),
                'zip',
                os.path.join(EXPORT_FOLDER, 'user_{}').format(request.user.id)
            )
            zip_file = open(
                os.path.join(EXPORT_FOLDER, 'user_exported_{}', 'compressed_{}.zip').format(request.user.id,
                                                                                            request.user.id), 'rb')
            response = HttpResponse(zip_file, content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename=name.zip'

            return response
        else:
            return JsonResponse({"agents": "No agents to export."})


class ImportAgentsManager(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    #TODO: Add permission class for agent import class

    def post(self, request):
        """
        {"zip_file":file}
        """

        # 1) read zip file and extract its content:
        try:
            zip_file = request.FILES["zip_file"]
        except:
            return JsonResponse({"error": "Expected zip_file."})

        path_to_user_folder = os.path.join(IMPORT_FOLDER, 'user_{}').format(request.user.id)
        try:
            shutil.rmtree(path_to_user_folder)
        except:
            os.makedirs(path_to_user_folder)

        # 2) extract zip file and import data to database
        zip_ref = zipfile.ZipFile(zip_file, 'r')
        zip_ref.extractall(path_to_user_folder)
        zip_ref.close()

        """ load agents.json file """
        try:
            agents_file = open(os.path.join(path_to_user_folder, 'agents.json'))
        except:
            return JsonResponse({"erreur": "Fichier agents.json non trouvé."})

        try:
            agents = json.load(agents_file)["Agents"]
        except:
            return JsonResponse({"erreur": "Fichier agents.json ne peut pas etre chargé correctement."})
        related_agent = Related_Agent.objects.create(name="Agent_Import_function")
        for agent in agents:
            serializer = serializers.AgentManagerSerializer(data=agent,
                                                            context={'request': self.request,
                                                                     'path_to_user_folder': path_to_user_folder})
            if serializer.is_valid():
                courantAgent = serializer.create(agent)
                courantAgent.related_agent = related_agent
                if 'is_main' in agent:
                    courantAgent.is_main = agent['is_main']
                courantAgent.save()
                if 'is_default' in agent and agent['is_default']:
                    courantAgent.is_default = True
                    courantAgent.save()
                    '''affect the created default_agent to all the existing users'''
                    users = UserProfile.objects.exclude(id=self.request.user.id)
                    for user in users:
                        UserPermissions.objects.create(
                            agent=courantAgent,
                            user_profile=user,
                            is_admin=False,
                            creating_access=False,
                            reading_access=True,
                            updating_access=False,
                            deleting_access=False,

                        )
                entities = defaultEntitys.GetEntitys(self)
                for entity in entities:
                    serializer = serializers.EntityManagerSerializer(data=entity,
                                                                     context={'request': self.request,
                                                                              'agentid': courantAgent.id})
                    if serializer.is_valid():
                        entityObj = serializer.save()
                        entityObj.is_default = True
                        entityObj.save()
            else:
                raise ValidationError(serializer.error_messages)

        return JsonResponse({"success": "OK"})


class RestoreAgentManager(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # TODO: class not yet tested
    # TODO: Add permission class for agent export class

    def post(self, request):
        """
        {"zip_file":file,
        "agent_id": agentID}
        """
        # 1) read zip file and extract its content:
        try:
            zip_file = request.FILES["zip_file"]
        except:
            return JsonResponse({"error": "Expected zip_file."})
        try:
            agent_id = request.data["agent_id"]
        except:
            return JsonResponse({"error": "Expected agent_id."})

        print("type agent_id", type(agent_id))
        if type(agent_id) != str:
            return JsonResponse({"error": "Expected integer."})
        try:
            agent = Agent.objects.get(id=agent_id)
        except:
            return JsonResponse({"error": "Agent not found "+str(agent_id)})

        path_to_user_folder = os.path.join(IMPORT_FOLDER, 'user_{}').format(request.user.id)
        try:
            shutil.rmtree(path_to_user_folder)
        except:
            os.makedirs(path_to_user_folder)

        # 2) extract zip file and import data to database
        zip_ref = zipfile.ZipFile(zip_file, 'r')
        zip_ref.extractall(path_to_user_folder)
        zip_ref.close()

        """ load agents.json file """
        agents_file = open(os.path.join(path_to_user_folder, 'agents.json'))
        try:
            agents = json.load(agents_file)["Agents"]
        except:
            return JsonResponse({"error": "Problème lors de la lecture du fichier agents.json"})

        if len(agents) > 1:
            return JsonResponse({"error": "Le fichier agents.json contient plus qu'un agent."})
        if len(agents) == 0:
            return JsonResponse({"error": "Aucun agent trouvé dans le fichier agents.json."})

        if len(agents) == 1:
            serializer = serializers.AgentManagerSerializer(data=agents[0],
                                                            context={'request': self.request,
                                                                     'path_to_user_folder': path_to_user_folder})
            if serializer.is_valid():
                # delete intents related to this agent
                intents = Intent.objects.filter(agent=agent_id)
                for intent in intents:
                    intent.delete()
                serializer.update(agent, agents[0])
            else:
                raise ValidationError(serializer.error_messages)

        return JsonResponse({"success": "OK"})




class GetAgentInfo(viewsets.ModelViewSet):

    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.GetAgentInfoSerializer
    permission_classes = (IsAuthenticated,permissions.AgentInfoPemissions)

    def get_queryset(self):
        agent=Agent.objects.filter(is_default=False)
        return(agent)

class AddQuestionManagerView(APIView):

    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.AddQuestionToIntent
    permission_classes = (IsAuthenticated,permissions.IntentPermissions)

    def post(self, request, agentid):

        serializer = self.serializer_class(data=request.data, context={'agentid': agentid}, many=True)

        if serializer.is_valid(raise_exception=True):

            return Response({"success": True})
        else:
            raise ValidationError(serializer.error_messages)

###############     ENTITY      ##################
"""Intent manager class"""
class EntityManagerView(viewsets.ModelViewSet):
    """Handle creating reading and updating intents"""

    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.EntityManagerSerializer
    permission_classes = (IsAuthenticated,permissions.IntentPermissions)
    #filter_backends = (filters.SearchFilter,)
    #search_fields = ('name',)
    #pagination_class = StandardIntentResultsSetPagination
    def create(self, request, *args, **kwargs):

        verif={"success":True}
        serializer = serializers.EntityManagerSerializer(data=self.request.data, context={'request': self.request, 'agentid': self.kwargs['agentid']})
        if serializer.is_valid():
            serializer.create(self.request.data)
            return Response({"sucess":"ok"})
        raise ValidationError(serializer.error_messages)

    def update(self, request, *args, **kwargs):
        serializer = serializers.EntityManagerSerializer(data=self.request.data, context={'request': self.request, 'agentid': self.kwargs['agentid']})
        if serializer.is_valid():
            instance = self.get_object()
            serializer.update(instance, self.request.data)
            return Response({"sucess":"ok"})
        raise ValidationError(serializer.error_messages)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object().id
        entity=self.get_object()
        agent = entity.agent
        if entity.is_default == True:
            raise Exception("Vous ne devez pas supprimer une entité par defaut")
        Entity.objects.filter(id=instance).delete()
        agent.status = "non entrainer"
        agent.save()
        return Response({"sucess":"ok"})

    def Sort_Entity(e):
        return e['id']
    def get_queryset(self):
        perm= UserPermissions.objects.filter(user_profile=self.request.user, is_active=True).values('agent')
        agentid= self.kwargs['agentid']
        agent= Agent.objects.filter(id__in =perm, id=agentid).values('pk')
        entity= Entity.objects.filter(agent__in =agent).order_by('id')
        #entity.sort(key=Sort_Entity)
        return (entity)



###############     ENTITY      ##################


class VideoUploadManagerView(viewsets.ModelViewSet):
    """Handle creating reading and updating intents"""

    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.UploadVideoManagerSerializer
    permission_classes = (IsAuthenticated,permissions.IntentPermissions)
    #filter_backends = (filters.SearchFilter,)
    #search_fields = ('name',)
    #pagination_class = StandardIntentResultsSetPagination
    def create(self, request, *args, **kwargs):

        verif={"success":True}
        serializer = serializers.UploadVideoManagerSerializer(data=self.request.data, context={'request': self.request, 'agentid': self.kwargs['agentid']})
        if serializer.is_valid():
            resp = serializer.create(self.request.data)
            return Response({"url":resp})
        raise ValidationError(serializer.error_messages)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object().id
        video=self.get_object()
        agent = video.agent
        # try:
        #     os.remove(video.video.path)
        # except Exception as e:
        #     pass
        Video.objects.filter(id=instance).delete()
        agent.status = "non entrainer"
        agent.save()
        return Response({"sucess":"ok"})

    def get_queryset(self):
        perm= UserPermissions.objects.filter(user_profile=self.request.user, is_active=True).values('agent')
        agentid= self.kwargs['agentid']
        agent= Agent.objects.filter(id__in =perm, id=agentid).values('pk')
        video= Video.objects.filter(agent__in =agent)
        return (video)

class AudioUploadManagerView(viewsets.ModelViewSet):
    """Handle creating reading and updating intents"""

    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.UploadAudioManagerSerializer
    permission_classes = (IsAuthenticated,permissions.IntentPermissions)
    #filter_backends = (filters.SearchFilter,)
    #search_fields = ('name',)
    #pagination_class = StandardIntentResultsSetPagination
    def create(self, request, *args, **kwargs):

        verif={"success":True}
        serializer = serializers.UploadAudioManagerSerializer(data=self.request.data, context={'request': self.request, 'agentid': self.kwargs['agentid']})
        if serializer.is_valid():
            resp = serializer.create(self.request.data)
            return Response({"url":resp})
        raise ValidationError(serializer.error_messages)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object().id
        audio=self.get_object()
        agent = audio.agent
        Audio.objects.filter(id=instance).delete()
        agent.status = "non entrainer"
        agent.save()
        return Response({"sucess":"ok"})

    def get_queryset(self):
        perm= UserPermissions.objects.filter(user_profile=self.request.user, is_active=True).values('agent')
        agentid= self.kwargs['agentid']
        agent= Agent.objects.filter(id__in =perm, id=agentid).values('pk')
        audio= Audio.objects.filter(agent__in =agent)
        return (audio)

""" Persistent Menu """
class MenuManagerView(viewsets.ModelViewSet):
    """Handle creating reading and updating intents"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, permissions.IntentPermissions)

    serializer_class = serializers.MenuManagerSerializer
    def create(self, request, *args, **kwargs):

        print(self.request.data)
        serializer = serializers.MenuManagerSerializer(data=self.request.data, context={'request': self.request, 'agentid': self.kwargs['agentid']})
        if serializer.is_valid():
            serializer.create(self.request.data)
            return Response({"sucess":"ok"})
        raise ValidationError(serializer.error_messages)

    def get_queryset(self):
        agentid = self.kwargs['agentid']
        menu = Menu.objects.filter(agent=agentid)
        return (menu)

    def update(self, request, *args, **kwargs):
        serializer = serializers.MenuManagerSerializer(data=self.request.data, context={'request': self.request, 'agentid': self.kwargs['agentid']})
        if serializer.is_valid():
            instance = self.get_object()
            serializer.update(instance, self.request.data)
            return Response({"sucess":"ok"})
        raise ValidationError(serializer.error_messages)

""" Persistent Menu with facebook api calls """
# class MenuManagerView(viewsets.ModelViewSet):
#     """Handle creating reading and updating intents"""
#
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated, permissions.IntentPermissions)
#
#     serializer_class = serializers.MenuManagerSerializer
#     def create(self, request, *args, **kwargs):
#
#         print(self.request.data)
#         serializer = serializers.MenuManagerSerializer(data=self.request.data, context={'request': self.request, 'agentid': self.kwargs['agentid']})
#         if serializer.is_valid():
#             serializer.create(self.request.data)
#             agentID = self.kwargs['agentid']
#             agent = Agent.objects.get(id=agentID)
#             menu = Menu.objects.filter(agent=agent)
#             if len(menu) > 0:
#
#                 # set get_stared button (Required before setting the persistent menu for any facebook page)
#                 get_started = GetStarted(agentID)
#                 res = get_started.GET()
#                 if res:
#                     # set the persistent menu
#                     # get the json format fo setting persistent menu on the facebook page associated to this agent
#                     menuObj = menu.first()
#                     menu_json = menu_persistent.persistent_menu_json(menuObj.id)
#                     persistent_menu = PersistentMenu(agentID)
#                     status_code = persistent_menu.POST(menu_json)
#                     if status_code == 200:
#                         return Response({"sucess": "ok"})
#                     else:
#                         return Response({"info": "Une erreur est survenu lors de la creation du menu persistent au niveau de la page sur facebook."})
#             else:
#                 return Response({"success": "ok"})
#         raise ValidationError(serializer.error_messages)
#
#     def get_queryset(self):
#         agentid = self.kwargs['agentid']
#         menu = Menu.objects.filter(agent=agentid)
#         return (menu)
#
#     def update(self, request, *args, **kwargs):
#         serializer = serializers.MenuManagerSerializer(data=self.request.data, context={'request': self.request, 'agentid': self.kwargs['agentid']})
#         if serializer.is_valid():
#             instance = self.get_object()
#             serializer.update(instance, self.request.data)
#
#             agentID = self.kwargs['agentid']
#             agent = Agent.objects.get(id=agentID)
#             menu = Menu.objects.filter(agent=agent)
#             if len(menu) > 0:
#
#                 # set get_stared button (Required before setting the persistent menu for any facebook page)
#                 get_started = GetStarted(agentID)
#                 res = get_started.GET()
#                 if res:
#                     # set the persistent menu
#                     # get the json format fo setting persistent menu on the facebook page associated to this agent
#                     menuObj = menu.first()
#                     menu_json = menu_persistent.persistent_menu_json(menuObj.id)
#                     persistent_menu = PersistentMenu(agentID)
#                     status_code = persistent_menu.POST(menu_json)
#                     if status_code == 200:
#                         return Response({"sucess": "ok"})
#                     else:
#                         return Response({"info": "Une erreur est survenu lors de la creation du menu persistent au niveau de la page sur facebook."})
#
#             else:
#                 return Response({"success": "ok"})
#
#         raise ValidationError(serializer.error_messages)
#
#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object().id
#         Menu.objects.filter(id=instance).delete()
#         agentID = self.kwargs['agentid']
#         menu = PersistentMenu(agentID)
#         status_code = menu.DELETE()
#         if status_code == 200:
#             print("ok")
#             return Response({"sucess":"ok"})
#         else:
#             return Response({"info": "Une erreur est survenu lors de la suppression du menu persistent au niveau de la page sur facebook."})


class PersistentMenuManagerView(APIView):
    """ Gets ID of agent and returns the menu (json) of this agent in the Facebook API format"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, permissions.IntentPermissions)

    def get(self, *args, **kwargs):

        try:
            agent = Agent.objects.get(id=self.kwargs['agentid'])
        except:

            return Response({"erreur": "Cet agent est peut etre supprimé."})

        menu = Menu.objects.filter(agent=agent)
        if len(menu) > 0:
            menu = menu.first()
            return Response(menu_persistent.persistent_menu_json(menu.id))
        else:
            return Response({"info": "Aucun menu n'est crée pour cet agent pour le moment."})

class GetMenuForWidget(viewsets.ModelViewSet):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, permissions.AgentMenuWidgetPermission)
    serializer_class = serializers.MenuManagerSerializer

    def get_queryset(self):
        try:
            agent = Agent.objects.get(id=self.kwargs['agentid'])
        except:

            return Response({"erreur": "Cet agent est peut etre supprimé."})

        menu = Menu.objects.filter(agent=agent)
        return (menu)

