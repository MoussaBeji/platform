from rest_framework import serializers
from commands.models import *
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class ProductManagerSerializer(serializers.ModelSerializer):
    categorieName = serializers.CharField(source= 'categorie.name', read_only=True)
    class Meta:
        model = Products
        fields = ['id', 'title', 'description', 'price', 'categorie','image', 'categorieName']

    def create(self, validated_data):
        categorie= Categories.objects.get(id=validated_data['categorie'])
        Products.objects.create(title=validated_data['title'],
                                description=validated_data['description'],
                                price=validated_data['price'],
                                categorie=categorie,
                                image=validated_data['image'],)


class CategorieManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ('id', 'name',)
    def create(self, validated_data):
        Categories.objects.create(name=validated_data['name'])



class CommandsManagerSerializer(serializers.ModelSerializer):
    productName = serializers.CharField(source= 'product.title', read_only=True)
    class Meta:
        model = Commands
        fields = ['id', 'table_id', 'quantity', 'total_price', 'status', 'product','productName']
        extra_kwargs = {'total_price':{'read_only': True}}
    def create(self, validated_data):
        product= Products.objects.get(id=validated_data['product'])
        totalprice = int(validated_data['quantity'])*float(product.price)
        Commands.objects.create(table_id=validated_data['table_id'],
                                quantity=validated_data['quantity'],
                                total_price=str(totalprice),
                                product=product,
                                status=validated_data['status'],)

