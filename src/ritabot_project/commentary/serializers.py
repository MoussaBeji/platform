from rest_framework import serializers
from commentary.models import *
from django.utils.translation import gettext_lazy as _
from AgentManager.models import Agent
from django.utils import timezone


class ExportCommentaryInfoManagerSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()
    gouvernorat = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()
    telephone = serializers.SerializerMethodField()
    date_update = serializers.SerializerMethodField()
    data_contact = serializers.SerializerMethodField()
    date_action = serializers.SerializerMethodField()
    class Meta:
        model = Commentary_Info
        fields = ['client','gouvernorat','region','telephone','besoin','source','data_contact','commercial'
                  ,'date_action','observation','prix','remarque','note','date_update']

        extra_kwargs = {
            'data_contact': {'read_only': True, 'required': False},
            'date_update': {'read_only': True, 'required': False},
        }
    def get_client(self, obj):
        return (obj.Commentary.client)
    def get_gouvernorat(self, obj):
        return (obj.Commentary.gouvernorat)
    def get_region(self, obj):
        return (obj.Commentary.region)
    def get_telephone(self, obj):
        return (obj.Commentary.telephone)
    def get_date_update(self, obj):
        try:
            date=obj.date_update.date()
            time=obj.date_update.time().replace(microsecond=0)
            returnred=str(date)+" à "+str(time)
        except:
            returnred=obj.date_update

        return (returnred)
    def get_data_contact(self, obj):
        try:
            date = obj.data_contact.date()
            time = obj.data_contact.time().replace(microsecond=0)
            returnred = str(date)+" à "+str(time)
        except:
            returnred=obj.date_contact

        return (returnred)
    def get_date_action(self, obj):
        try:
            date = obj.date_action.date()
            time = obj.date_action.time().replace(microsecond=0)
            returnred = str(date)+" à "+str(time)
        except:
            returnred=obj.date_action

        return (returnred)


class CommentaryInfoManagerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Commentary_Info
        fields = ['id', 'besoin','source','data_contact','commercial'
                  ,'date_action','observation','prix','remarque','note','date_update']

        extra_kwargs = {
            'data_contact': {'read_only': True, 'required': False},
            'date_update': {'read_only': True, 'required': False},
        }

class CommentaryManagerSerializer(serializers.ModelSerializer):
    commentary_info= CommentaryInfoManagerSerializer(many=True, required=False)
    class Meta:
        model = Commentary
        fields = ['id', 'client_id', 'client', 'gouvernorat', 'region','telephone','commentary_info','data_creation','date_update']

        extra_kwargs = {
            'data_creation': {'read_only': True, 'required': False},
            'date_update': {'read_only': True, 'required': False},
        }

    def create(self, validated_data):
        agentID = self.context['agentid']

        try:
            agent = Agent.objects.get(pk=agentID)
        except(TypeError, ValueError, OverflowError, Agent.DoesNotExist):
            raise serializers.ValidationError({'Erreur': [_("Cet agent n'existe pas")]})
        client=None
        try:
            client = Commentary.objects.get(client_id=validated_data['client_id'])
        except:
            pass

        if client:
            if 'client' in validated_data and validated_data['client']:
                client.client=validated_data['client']
                client.save()
            if 'gouvernorat' in validated_data and validated_data['gouvernorat']:
                client.gouvernorat = validated_data['gouvernorat']
                client.save()
            if 'region' in validated_data and validated_data['region']:
                client.region = validated_data['region']
                client.save()
            if 'telephone' in validated_data and validated_data['telephone']:
                client.telephone = validated_data['telephone']
                client.save()
            if 'commentary_info_list' in validated_data and validated_data['commentary_info_list']:
                print(validated_data['commentary_info_list'])
                Commentary_Info.objects.create(**validated_data['commentary_info_list'][0], Commentary=client)


        else:

            commObj=Commentary.objects.create(
                client_id=validated_data['client_id'],client=validated_data['client'], gouvernorat=validated_data['gouvernorat'],
                region=validated_data['region'], telephone=validated_data['telephone'], agent=agent
            )
            if 'commentary_info_list' in validated_data and validated_data['commentary_info_list']:
                print(validated_data['commentary_info_list'])
                Commentary_Info.objects.create(**validated_data['commentary_info_list'][0], Commentary=commObj)

    def update(self, instance, validated_data, *args, **kwargs):
        #comm_info=instance.commentary_info
        request = self.context.get("request")
        comm_infoe= request.data['commentary_info']

        for comm in comm_infoe:

            try:
                comm_instance = Commentary_Info.objects.get(pk=comm['id'])
            except(TypeError, ValueError, OverflowError, Commentary_Info.DoesNotExist):
                raise serializers.ValidationError({'Erreur': [_("Objet de commentaire est introuvable")]})
            comm_instance.besoin=comm['besoin']
            comm_instance.source=comm['source']
            comm_instance.commercial=comm['commercial']
            comm_instance.date_action=comm['date_action']
            comm_instance.observation=comm['observation']
            comm_instance.prix=comm['prix']
            comm_instance.remarque=comm['remarque']
            comm_instance.note=comm['note']
            comm_instance.save()
        return instance


"""
, besoin=validated_data['besoin'],
                source=validated_data['source'], commercial=validated_data['commercial'],
                date_action=validated_data['date_action'],
                observation=validated_data['observation'], prix=validated_data['prix'], remarque=validated_data['remarque'],
                note=validated_data['note'],
"""