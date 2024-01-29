from django.shortcuts import render
from rest_framework import viewsets
from ProfileManager import serializers
from ProfileManager import models
from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.views import APIView, View
from rest_framework import filters
from django.contrib.auth.hashers import check_password
from ritabot.settings import *
"""     Response types        """
from rest_framework.response import Response
from django.http import HttpResponse
from django.http import JsonResponse

"""     Permissions and token import modules    """
from rest_framework.authentication import TokenAuthentication
from ProfileManager import permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

"""     For messages, token and reset password       """
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail


class UserCreateProfile(APIView):
    """Handle create new profile"""

    serializer_class = serializers.UserCreateProfileSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        return JsonResponse({"success": True}, safe=False)




class UserProfileManager(viewsets.ModelViewSet):
    """Handle update and delete profiles"""

    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.UserProfileSerializer
    queryset = models.UserProfile.objects.all()
    permission_classes = ( IsAuthenticated, permissions.UpdateOwnProfile,)

    def get_queryset(self):
          return models.UserProfile.objects.filter(username=self.request.user.username)


class checkstatus(APIView):
    def post(self, request, *args, **kwargs):
        return JsonResponse({"success": 'ok'}, safe=False)

    def get(self, request, *args, **kwargs):
        return JsonResponse({"success": 'ok'}, safe=False)
class UserPasswordManager(APIView):
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.UserPasswordManagerSerializer
    permission_classes = ( IsAuthenticated, permissions.UpdateOwnPassword,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        if serializer.is_valid():

            currentPassword = serializer.validated_data.get('ancienPassword')
            newPassword = serializer.validated_data.get('nouvPassword')

            if check_password(currentPassword, request.user.password):
                request.user.set_password(newPassword)
                request.user.save()
                Token.objects.filter(user=request.user).delete()
                return JsonResponse({"success": True}, safe=False)
            else:
                return JsonResponse({"success": 'mot de passe inccorecte'}, safe=False)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginApiView(ObtainAuthToken):
    """Handle creating user authentication and generate tokens"""
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = serializers.CustumAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response([{'token': token.key}, {
        'id': token.user.id,
        'username': token.user.username,
        'email': token.user.email,
        'first_name': token.user.first_name,
        'last_name': token.user.last_name,
        'company': token.user.company,
        'is_superuser': token.user.is_superuser}])


class ForgetPassword(APIView):
    serializer_class = serializers.ForgetPasswordSerializer

    def post(self, request):
        serializers = self.serializer_class(data=request.data)
        if serializers.is_valid():

            email = serializers.validated_data.get('email')
            try:
                user = models.UserProfile.objects.get(email =email)
            except(TypeError, ValueError, OverflowError, models.UserProfile.DoesNotExist):
                user = None
            if user is not None:
                current_site = get_current_site(request)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = account_activation_token.make_token(user)
                mail_subject = 'Reset your password.'
                activation_link = urlServer+"passwordreset/{0}/{1}".format(uid , token)
                message = "Hello {0},\n {1}".format(user.first_name, activation_link)
                to_email = user.email
                send_mail(
                    mail_subject,
                    message,
                    EMAIL_HOST_USER,
                    [to_email],
                    fail_silently=False,
                )
                return JsonResponse({'success': True}, safe=False)
            else:
                return JsonResponse({'success': False}, safe=False)
        else:
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateProfile(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = models.UserProfile.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, models.UserProfile.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            # activate user and login:
            user.is_active = True
            user.save()
            return JsonResponse({'success': True}, safe=False)
        else:
            return JsonResponse({'success': False}, safe=False)


class ResetPassword(APIView):
    serializer_class = serializers.ResetPasswordSerializer

    def post(self, request, uidb64, token):

        serializers = self.serializer_class(data=request.data)
        if serializers.is_valid():

            password = serializers.validated_data.get('password')
            try:
                uid = force_text(urlsafe_base64_decode(uidb64))
                user = models.UserProfile.objects.get(pk=uid)
            except(TypeError, ValueError, OverflowError, models.UserProfile.DoesNotExist):
                user = None
            if user is not None and account_activation_token.check_token(user, token):
                user.set_password(password)
                user.save()
                return JsonResponse({'success': True}, safe=False)
            else:
                return JsonResponse({'success': False}, safe=False)
        return JsonResponse({'success': False}, safe=False)