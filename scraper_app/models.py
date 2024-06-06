from django.db import models
import os

# Create your models here.

class Substances(models.Model):
    names = models.JSONField(default=list, blank=True, primary_key=False)
    formula = models.CharField(max_length=1000, blank=True,primary_key=False)
    iupac_names = models.JSONField(default=list, blank=True, primary_key=False)
    smiles = models.CharField(max_length=1000, blank=True,primary_key=False)
    inchi = models.CharField(max_length=1000, blank=True,primary_key=False)
    inchi_key = models.CharField(max_length=1000, blank=True,primary_key=False)
    molecular_mass = models.FloatField(blank=True,primary_key=False)
    cas_num = models.CharField(max_length=1000, default="0", blank=True,primary_key=False)
    categories = models.JSONField(default=list, blank=True,primary_key=False)
    source = models.JSONField(blank=True,primary_key=False)
    validated = models.BooleanField(default=False, blank=True,primary_key=False)
    deleted = models.BooleanField(default=False)
    last_modified = models.DateTimeField(blank=True, auto_now=True,primary_key=False)
    version = models.CharField(max_length=200, default="0", blank=True, primary_key=False)
    details = models.JSONField(blank=True, primary_key=False)

class Store_exchange_json(models.Model):
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to="./files_from_others/")