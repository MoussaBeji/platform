from rest_framework import serializers
from datetime import datetime
from ProfileManager import models
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.contrib.auth import authenticate
from operator import itemgetter
from ritabot.settings import *
""" For sending email, generate token and hash the user ID import the following custumized packages """
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token
from django.core.mail import send_mail
from django.template.loader import render_to_string

"""     End importing send email packages    """



class UserProfileSerializer(serializers.ModelSerializer):
    """Serializers a user profile object"""

    class Meta:
        model = models.UserProfile
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'company', 'password')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'}
            }
        }

    def update(self, instance, validated_data):
        """OverWrite the update user function"""
        for attr, value in validated_data.items():
            if attr == 'password':
                pass
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        setattr(instance, 'last_login', datetime.now())
        instance.save()
        return instance


class UserCreateProfileSerializer(serializers.Serializer):
    """Serializers a user profile object"""

    username = serializers.CharField(label=_("username"))
    email = serializers.CharField(label=_("email"))
    first_name = serializers.CharField(label=_("first_name"))
    last_name = serializers.CharField(label=_("last_name"))
    company = serializers.CharField(label=_("company"))
    password = serializers.CharField(
        label=_("password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, validated_data):
        """Create new user and send the validation email"""
        is_username_exist = models.UserProfile.objects.filter(username=validated_data['username'])
        is_email_exist = models.UserProfile.objects.filter(email=validated_data['email'])
        if (len(is_username_exist) != 0):
            raise serializers.ValidationError({'username':
                                            [_("Ce nom d'utilisateur est deja utilisé, essayer avec un autre")]})

        if (len(is_email_exist) != 0):
            raise serializers.ValidationError({'email':
                                                [_("Cet adresse email est deja utilisé, essayer avec une autre")]})

        user = models.UserProfile.objects.create_user(
            username=validated_data['username'],
            email = validated_data['email'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            company = validated_data['company'],
            password=validated_data['password'],
        )

        """Send an email to the specified user with the activation token"""
        mail_subject ='Bienvenue sur RITABOT ! Merci de confirmer votre e-mail'
        current_site = get_current_site(self.context.get('request'))
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        activation_link = "{0}activate/{1}/{2}".format(urlServer,uid , token)
        message = "Hello {0},\n Please find below the activation link for your account. \n {1}"\
            .format(user.username, activation_link)
        html_message = render_to_string("email_insc.html", {"first_name": user.first_name, "last_name": user.last_name, "activation_link":activation_link})

        to_email = validated_data['email']
        send_mail(
            mail_subject,
            message,
            EMAIL_HOST_USER,
            [to_email],
            fail_silently=False,
            html_message=html_message,
        )
        return user


class UserPasswordManagerSerializer(serializers.Serializer):
    """Handle change password for the connected user"""

    ancienPassword = serializers.CharField(
        label=_("ancienPassword"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    nouvPassword = serializers.CharField(
        label=_("nouvPassword"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )


class CustumAuthTokenSerializer(serializers.Serializer):
    """Class serializer for log in"""

    username = serializers.CharField(label=_("username"))
    password = serializers.CharField(
        label=_("password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        """ Get the username from the email"""
        if username.find('@') != 1:
            val = models.UserProfile.objects.filter(email=username).values('username')
            if len(val) == 1:
                usernameList = list(map(itemgetter('username'), val))
                username = usernameList[0]

        userList = models.UserProfile.objects.filter(username=username)
        if (len(userList) == 0):
            msg = _('Utilisateur inconnue ')
            raise serializers.ValidationError(msg)
        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)

            '''update the latest login of the users'''
            models.UserProfile.objects.filter(email=username).update(last_login= datetime.now())
            if not user:
                msg = _('mot de passe incorrecte ')
                raise serializers.ValidationError({ 'password': [_('mot de passe incorrecte')]})
        else:
            msg = _('vous devez specifier un nom d\'utilisateur et une mot de passe valide')
            raise serializers.ValidationError(msg)

        attrs['user'] = user
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    """Serializers a name field for testing our APIView"""

    password = serializers.CharField(
        label=_("password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )


class ForgetPasswordSerializer(serializers.Serializer):
    """Serializers a name field for testing our APIView"""

    email = serializers.CharField(max_length=50)

