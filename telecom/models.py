from django.db import models

# Create your models here.
from django.db import models


class Card(models.Model):
    phone = models.CharField(max_length=20, default='')
    password = models.CharField(max_length=20, default='')
    encryptPassword = models.CharField(max_length=50, default='')
    icc_id = models.CharField(max_length=40, default='')
    user = models.CharField(max_length=40, default='')
    net = models.CharField(max_length=100, default='')
    remark = models.CharField(max_length=100, default='')
    sort = models.IntegerField(default=None, null=True)
    update = models.DateTimeField(auto_now=True)


class Votes(models.Model):
    info = models.TextField(max_length=50000, default='')
    time = models.IntegerField(default=None, null=True)


class Online(models.Model):
    identity = models.CharField(max_length=32, default='')
    update = models.DateTimeField(auto_now=True)
    arrDrop = models.CharField(max_length=100, default='')

class Download(models.Model):
    url = models.CharField(max_length=100,unique=True)
