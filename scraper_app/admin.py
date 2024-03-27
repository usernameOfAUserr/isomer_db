from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Substance, json_substance

admin.site.register(Substance)
admin.site.register(json_substance)