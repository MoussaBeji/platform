from django.db import models
import uuid
import os


def imageFilePath(instance, filename):
    """Generate file path for new mage/file"""

    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('upoloads/image_commands/', filename)

class Categories(models.Model):

    name = models.CharField(max_length=256, null=True, blank=True)
    def __str__(self):
        return self.name


class Products(models.Model):

    title = models.CharField(max_length=256, null=True, blank=True)
    description = models.TextField(blank=True, null=True, default="None")
    price = models.CharField(max_length=256, null=True, blank=True)
    categorie=models.ForeignKey(Categories, on_delete=models.CASCADE, related_name='categorie', blank=True, null=True)
    image = models.ImageField(default='upoloads/image/65ca9c88-115d-4837-b24f-75046046cbc0.png', null=True, upload_to=imageFilePath)
    def __str__(self):
        return self.title

class Commands(models.Model):

    table_id = models.CharField(max_length=256, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    total_price = models.CharField(max_length=256, null=True, blank=True)
    status = models.CharField(max_length=256, null=True, blank=True)
    product=models.ForeignKey(Products, on_delete=models.CASCADE, related_name='product', blank=True, null=True)
    def __str__(self):
        return self.table_id

