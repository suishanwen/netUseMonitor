from django.db import models

# Create your models here.
from django.db import models


class Card(models.Model):
    phone = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    net = models.CharField(max_length=100)
