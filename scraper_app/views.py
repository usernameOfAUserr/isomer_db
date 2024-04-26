import json
from .getData import getData
from django.shortcuts import render
import os
import logging
import requests
from scraper_app.models import Substances
from django.http import HttpResponse, JsonResponse
import time
import shutil
import re
from bs4 import BeautifulSoup
from .getReachableUrls import getReachableUrls
from django.template.defaultfilters import stringfilter
import aiohttp, asyncio

# Create your views here.


getDataObject = getData()
JS = Substances.objects.all()
keys = [field.name for field in Substances._meta.fields]
del keys[0]

def scraper(request):
    if request.method == "POST":
        requested = []
        selected = request.POST.get('select')
        searched = request.POST.get('search_field')
        if selected == "molecular_mass":
            toleranz = request.POST.get("abweichung")
            start = float(searched)-float(toleranz)
            end = float(searched)+float(toleranz)
            requested = Substances.objects.filter(molecular_mass__range=[start,end])
        elif selected == "smiles":
            if Substances.objects.filter(smiles=searched) is not None:
                requested = Substances.objects.filter(smiles=searched)
            else:
                request = None
        elif selected == "formular":
            requested = []
            format = ".*" + searched + ".*"
            compare_regex = re.compile(format)
            for formular in JS:
                if compare_regex.search(formular.formular) is not None:
                    requested.append(formular)
        elif selected == "names":
            requested = []
            for names in JS:
                if searched in names.names:
                    requested.append(names)
        elif selected == "iupac_name":
            requested = []
            for names in JS:
                if searched in names.iupac_name:
                    requested.append(names)        
        elif selected == "cas_num":
            cas_num_results = Substances.objects.filter(cas_num=searched)
            requested.append(cas_num_results)

        elif selected == "category":
            category_results = Substances.objects.filter(category__icontains=searched)
            requested.append(category_results)

        elif selected == "source_url":
            source_url_results = Substances.objects.filter(source_url__icontains=searched)
            requested.append(source_url_results)

        elif selected == "source_name":
            source_name_results = Substances.objects.filter(source_name__icontains=searched)
            requested.append(source_name_results)

        elif selected == "valid":
            valid_results = Substances.objects.filter(valid=searched)
            requested.append(valid_results)

        elif selected == "deleted":
            deleted_results = Substances.objects.filter(deleted=searched)
            requested.append(deleted_results)

        elif selected == "version":
            version_results = Substances.objects.filter(version=searched)
            requested.append(version_results)

        elif selected == "details":
            details_results = Substances.objects.filter(details__icontains=searched)
            requested.append(details_results)
    
        else:
            requested = None
        return render(request, "scraper.html",{
            "answer": requested, "selected":selected,
                        "keys":keys,

        })
    else:
        db = Substances.objects.all()
        return render(request,"scraper.html",{
            "db": db, "answer": None,
            "keys":keys,
        })


def reset_database(request):
    getDataObject.start()
    return HttpResponse("Database was fully restored")
    
def request_how_many_json_file(request):
    progress = getDataObject.getProgress()
    return JsonResponse({"progress":progress})
    

def search_for_newcomers(request):
    new_ones = getReachableUrls()
    print("stroed in db")
    return JsonResponse({"newSubstances": new_ones})

################################################################
#Get joke

async def get_witz_asynchron(url):
    async with aiohttp.ClientSession() as session:  
        try:
            async with session.get(url) as response:
                data = await response.json()
                witz = data[0]["text"]
                return witz
        except Exception as e:  
            return {"error": str(e)}

async def get_witz_task(session, url):
    async with session.get(url) as response:
        data = await response.json()
        witz = data[0]["text"]
        return witz

def get_witz(request):
    url = "https://witzapi.de/api/joke/"
    witz = asyncio.run(get_witz_asynchron(url))  
    return JsonResponse({"witz": witz})
#####################################################################
