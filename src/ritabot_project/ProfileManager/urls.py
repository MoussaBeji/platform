from django.urls import path, include
from ProfileManager import views
from rest_framework.routers import DefaultRouter



router = DefaultRouter()
router.register('userprofile', views.UserProfileManager,base_name='userprofile')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.UserLoginApiView.as_view()),
    path('inscription/', views.UserCreateProfile.as_view()),
    path('activate/<str:uidb64>/<str:token>/', views.ActivateProfile.as_view(), name='activate'),
    path('forgetpassword/', views.ForgetPassword.as_view(), name='forget'),
    path('passwordreset/<str:uidb64>/<str:token>/', views.ResetPassword.as_view(), name='reset'),
    path('changepassword/', views.UserPasswordManager.as_view(), name='changePassword'),
    path('check_status/', views.checkstatus.as_view(), name='checkstatus'),
]
