from django.urls import path, include
from commands import views
from rest_framework.routers import DefaultRouter



router = DefaultRouter()
router.register('categorieslist', views.CategorieManagerView,base_name='userprofile')
router.register('productslist', views.ProductManagerView,base_name='userprofile')
router.register('commandslist', views.CommandsManagerView,base_name='userprofile')

urlpatterns = [
    path('', include(router.urls)),
]