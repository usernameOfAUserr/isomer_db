from django.db import models
import os

# Create your models here.

class Substance(models.Model):
    names = models.CharField(max_length=500,default="not_known")
    iupac_names = models.CharField(max_length=500,default="not_known")
    id = models.IntegerField(primary_key=True)
    formular = models.CharField(max_length=500, default="not_known")
    molecular_weight = models.FloatField()
    inchl = models.CharField(max_length=500,default="not_known")
    inchl_key = models.CharField(max_length=100,default="not_known")
    smiles = models.CharField(max_length=100,default="not_known")
    category_tag = models.CharField(max_length=100,default="not_known")
    validation_message = models.CharField(max_length=300,default="")

class json_substance(models.Model):
    all = models.JSONField()
