from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from AgentManager.models import Agent
from external_api.models import *



class FormationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Formation
        fields = ['id', 'formation', 'date_create', 'date_update']
        extra_kwargs = {'date_create': {'read_only': True},
                        'date_update': {'read_only': True}}


class StudentEnrollmentSerializer(serializers.ModelSerializer):
    formations = FormationSerializer(many=True, required=False)
    formation_name = serializers.CharField(max_length=300, read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name', 'gender','email','phone_number', 'date_create', 'date_update', 'formations', 'formation_name']
        extra_kwargs = {'date_create': {'read_only': True},
                        'date_update': {'read_only': True},
                        'gender': {'read_only': True},

                        }

    def create(self, validated_data, *args, **kwargs):

        try:
            first_name = validated_data['first_name']
            last_name = validated_data['last_name']
            email = validated_data['email']
            phone_number = validated_data['phone_number']
            formation_name = validated_data['formation_name']
        except:
            raise serializers.ValidationError({'Erreur': [_("Json invalide.")]})

        agentID = self.context['agentid']

        try:
            agent = Agent.objects.get(id=agentID)
            print(agent)
        except:
            raise serializers.ValidationError({'Erreur': [_("Agent non found.")]})

        try:
            formation = Formation.objects.get(formation=validated_data["formation_name"], agent=agent)
        except:
            formation = Formation.objects.create(formation=validated_data["formation_name"], agent=agent)


        students = Student.objects.filter(email=validated_data["email"], agent=agent)
        if len(students) > 0:
            #student with this email exists, update details
            student = students[0]
            student.first_name = validated_data["first_name"]
            student.last_name = validated_data["last_name"]
            student.phone_number = validated_data["phone_number"]
            student.save()
        else:
            try:
                # create new student
                del validated_data["formation_name"]
                print("validated_data :", validated_data)
                student = Student.objects.create(agent=agent, **validated_data)
            except Exception as e:
                print("e :", e)
                raise serializers.ValidationError({'Erreur': [_("Vous devez vérifier la création du Student.")]})


        # create enrollment student on the course
        Enrollment.objects.create(student=student, formation=formation)

        return JsonResponse({"success": True})