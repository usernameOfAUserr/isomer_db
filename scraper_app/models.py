from django.db import models
import os

# Create your models here.

class Substances(models.Model):
    names = models.JSONField(default=list, blank=True, primary_key=False)
    formular = models.CharField(max_length=1000, blank=True,primary_key=False)
    iupac_name = models.JSONField(default=list, blank=True, primary_key=False)
    smiles = models.CharField(max_length=1000, blank=True,primary_key=False)
    inchi = models.CharField(max_length=1000, blank=True,primary_key=False)
    inchi_key = models.CharField(max_length=1000, blank=True,primary_key=False)
    molecular_mass = models.FloatField(blank=True,primary_key=False)
    cas_num = models.IntegerField(max_length=1000, blank=True,primary_key=False)
    category = models.JSONField(default=list, blank=True,primary_key=False)
    source_url = models.CharField(max_length=300, default="Pihkal", blank=True,primary_key=False)
    source_name = models.CharField(max_length=200, default="PIKHAL", blank=True,primary_key=False)
    valid = models.BooleanField(default=False, blank=True,primary_key=False)
    deleted = models.BooleanField(default=False)
    last_changed_at = models.DateTimeField(blank=True, auto_now_add=True,primary_key=False)
    version = models.FloatField(default=0.0, blank=True,primary_key=False)
    details = models.JSONField(blank=True,default=list,primary_key=False)
