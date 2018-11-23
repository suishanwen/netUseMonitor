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
    sort = models.IntegerField(max_length=3)
    update = models.DateTimeField(auto_now=True)
