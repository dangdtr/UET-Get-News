from django.db import models
import django.utils.timezone

from dwnpptool.settings import TIME_ZONE

# Create your models here.

 
class Nws(models.Model):
    id = models.BigIntegerField(primary_key=True)
    title = models.CharField(max_length=200)
    nws_url = models.CharField(max_length=200)
    img_url = models.CharField(max_length=200)
    time = models.DateTimeField(default=django.utils.timezone.now)#, auto_now_add=True)

    def __str__(self):
        return self.title
    
class StpNws(models.Model):
    id = models.BigIntegerField(primary_key=True)
    title = models.CharField(max_length=200)
    nws_url = models.CharField(max_length=200)
    img_url = models.CharField(max_length=200)

    def __str__(self):
        return self.title