from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Substances, Store_exchange_json

admin.site.register(Substances)
admin.site.register(Store_exchange_json)