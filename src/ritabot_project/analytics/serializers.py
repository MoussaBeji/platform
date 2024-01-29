from rest_framework import serializers
from analytics.models import *
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import json
class ConversationManagerSerializer(serializers.ModelSerializer):
    intentName = serializers.CharField(source='outputIntent.name')

    class Meta:
        model = Conversation
        fields = ('id', 'inputMsg', 'outputIntent', 'outputRate', 'date','intentName',)
        extra_kwargs = {'date': {'read_only': True},
                        'outputIntent': {'required': False}}

class AnalyticsSerializer(serializers.ModelSerializer):

    agentStats = ConversationManagerSerializer(many=True, required=False)

    class Meta:
        model=AgentStats
        fields = ['id', 'sessionID', 'chaine', 'startTime', 'endTime' ,'adresseIP' ,'country' ,'platform' ,'browser', 'agent', 'agentStats']
        extra_kwargs = {'startTime': {'read_only': True},
        'endTime': {'read_only': True},
        'agent': {'read_only': True}}

    def create(self, validated_data, infoUser=None):

        agentID = self.context['agentid']

        try:
            agent=Agent.objects.get(pk=agentID)
        except(TypeError, ValueError, OverflowError, Agent.DoesNotExist):
            raise serializers.ValidationError({'Erreur': [_("Cet agent n'existe pas")]})

        if 'agentStats' in validated_data and validated_data['agentStats']:
            conversations = validated_data.pop('agentStats')
        else:
            raise serializers.ValidationError({'Erreur': [_("Vous devez inserer une conversation dans cet objet")]})
        agentStats=None
        try:
            agentStats = AgentStats.objects.get(agent=agent, info_user=infoUser, sessionID=validated_data['sessionID'])
        except:
            pass

        if not agentStats:

            try:

                agentStats= AgentStats.objects.create(agent=agent, info_user=infoUser, **validated_data)

            except:
                raise serializers.ValidationError({'Erreur': [_("Vous devez verifier la creation de l'objet agentStats")]})


        for conversation in conversations:

            if 'outputIntent' in conversation and conversation['outputIntent']:
                intentNameobj = conversation.pop('outputIntent')
                intentName = intentNameobj['name']

            else:
                raise serializers.ValidationError({'Erreur': [_("Vous devez specifier une reponse ")]})
            try:
                intentObj = Intent.objects.get(name=intentName, agent=agent)
            except:
                raise serializers.ValidationError({'Erreur': [_("intent invalide ")]})

            if not (intentObj):
                raise serializers.ValidationError(
                    {'Erreur': [_("Vous devez specifier une intent valide et appartienne à l'agent ")]})

            conv = Conversation.objects.create(outputIntent=intentObj, agentStats=agentStats, **conversation)

        agentStats.endTime=timezone.now()
        agentStats.save()
        return agentStats


class ExternalInfoManagerSerializer(serializers.ModelSerializer):
    payload = serializers.SerializerMethodField()

    class Meta:
        model=ExternalInfo
        fields = [ 'payload']
        extra_kwargs = {'payload': {'required': False}}

    def get_payload(self, obj):
        import json
        return json.loads(obj.payload.replace("'", '"'))



class UsersManagerSerializer(serializers.ModelSerializer):

    external_info = ExternalInfoManagerSerializer(many=False, required=False)

    class Meta:
        model=InfoUser
        fields = ['id', 'first_name', 'last_name', 'gender', 'client_id' ,'page_id' ,'access_token' ,'creation_date', 'external_info']
        extra_kwargs = {'creation_date': {'read_only': True},
        'first_name': {'read_only': True},
        'last_name': {'read_only': True},
        'gender': {'read_only': True},
        'page_id': {'read_only': True},
        'access_token': {'read_only': True},
        'client_id': {'read_only': True},
        }

    def update(self, instance, validated_data):
        print('received object', validated_data)
        od=validated_data.get('external_info')
        print(od['payload'])
        for key, value in od.items():
            print(key, value)




            # info=instance.external_info
        # if not info:
        #     objinfo=ExternalInfo.objects.create(
        #         payload=json.dumps(payload)
        #
        #     )
        #     instance.external_info=objinfo
        #     instance.save()
        # else:
        #     payload=json.dumps(payload)
        #     info.save()
        return instance



class UserAnalyticsSerializer(serializers.ModelSerializer):

    sessions = AnalyticsSerializer(many=True, required=False)
    external_info = ExternalInfoManagerSerializer(many=False, required=False, read_only=True)

    class Meta:
        model=InfoUser
        fields = ['id', 'first_name', 'last_name', 'gender', 'client_id' ,'page_id' ,'access_token' ,'creation_date', 'external_info', 'sessions']
        extra_kwargs = {'creation_date': {'read_only': True}
        }

    def create(self, validated_data):
        print('received object', validated_data)
        agentID = self.context['agentid']
        print('###', validated_data)
        try:
            agent=Agent.objects.get(pk=agentID)
        except(TypeError, ValueError, OverflowError, Agent.DoesNotExist):
            raise serializers.ValidationError({'Erreur': [_("Cet agent n'existe pas")]})

        if 'sessions' in validated_data and validated_data['sessions']:
            sessions = validated_data.pop('sessions')
        else:
            raise serializers.ValidationError({'Erreur': [_("Vous devez inserer une ou plusieurs sesions(s) dans cet objet")]})
        infoUser=None
        try:
            infoUser = InfoUser.objects.get(agent=agent, client_id=validated_data['client_id'])
        except:
            pass
        if not infoUser:
            try:

                infoUser= InfoUser.objects.create(agent=agent, **validated_data)

            except:
                raise serializers.ValidationError({'Erreur': [_("Vous devez verifier la creation de l'objet Info_User")]})

        infoUser.save()
        for session in sessions:

            new_session=AnalyticsSerializer.create(self,session, infoUser)
        return infoUser


