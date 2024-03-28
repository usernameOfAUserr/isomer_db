import json
from .getData import start
from django.shortcuts import render
import os
import logging
import requests
from scraper_app.models import Substance,json_substance
from django.http import JsonResponse
import time
import shutil
import re
from bs4 import BeautifulSoup
from .getReachableUrls import getReachableUrls
from django.template.defaultfilters import stringfilter

# Create your views here.

def scraper(request):
    if request.method == "POST":
        JS = Substance.objects.all()
        selected = request.POST.get('select')
        searched = request.POST.get('search_field')
        if selected == "massebereich":
            toleranz = request.POST.get("abweichung")
            start = float(searched)-float(toleranz)
            end = float(searched)+float(toleranz)
            requested = Substance.objects.filter(molecular_weight__range=[start,end])
        if selected == "SMILES":
            if Substance.objects.filter(smiles=searched) is not None:
                requested = Substance.objects.filter(smiles=searched)
            else:
                request = None
        if selected == "summenformel":
            requested = []
            format = ".*" + searched + ".*"
            compare_regex = re.compile(format)
            for formular in JS:
                if compare_regex.search(formular.formular) is not None:
                    requested.append(formular)
        if requested is None:
            requested = None
        return render(request, "scraper.html",{
            "answer": requested, "selected":selected,
        })
    else:
        db = Substance.objects.all()
        return render(request,"scraper.html",{
            "db": db, "answer": None
        })



def add_all_to_db(request):
    json_source_folder = ".\\response_data"
    if os.path.exists(json_source_folder) and os.path.isdir(json_source_folder):
        for file_name in os.listdir(json_source_folder):
            new_file_name = os.path.join(json_source_folder, file_name)
            with open(new_file_name, "r") as json_file:
                json_content = json.load(json_file)
                file_name = Substance(names=json_content["names"], iupac_names=json_content["iupac_name"], id=json_content["index"], formular=json_content["formular"],
                                      molecular_weight=json_content["molecular_weight"], inchl=json_content["inChl"], inchl_key=json_content["InChl_Key"], smiles=json_content["SMILES"],
                                      category_tag=json_content["category"])
                file_name.save()
        db = json_substance.objects.all()
        return render(request, "scraper.html",{
            "db": db
        })

def reset_database(request):

    json_source_folder = ".\\response_data"
    try:
        shutil.rmtree(json_source_folder)
    except:
        pass
    start()
    add_all_to_db(request)
    
def request_how_many_json_file(request):
    json_source_folder = ".\\response_data"
    try:
        how_many = 0
        dir = os.listdir(json_source_folder)
        for files in dir:
            how_many = how_many + 1
        progress = (how_many / 14500) * 100
        return JsonResponse({"progress":progress})
    except:
        print("no dir there")

def search_for_newcomers(request):
    new_ones = getReachableUrls()
    print("looking for new substances completed, begining integration")
    json_source_folder = "new_ones"
    if os.path.exists(json_source_folder) and os.path.isdir(json_source_folder):
        for file_name in os.listdir(json_source_folder):
            new_file_name = os.path.join(json_source_folder, file_name)
            with open(new_file_name, "r") as json_file:
                json_content = json.load(json_file)
                file_name = Substance(names=json_content["names"], iupac_names=json_content["iupac_name"], id=json_content["index"], formular=json_content["formular"],
                                      molecular_weight=json_content["molecular_weight"], inchl=json_content["inChl"], inchl_key=json_content["InChl_Key"], smiles=json_content["SMILES"],
                                      category_tag=json_content["category"], validation_message=json_content["validation"])   
                file_name.save()
    print("stroed in db")
    return JsonResponse({"newSubstances": new_ones})

def get_witz(request):
    parameters ={
        "limit":1,
        "category":"funny",
        "language":"de"
    }
    url = "https://witzapi.de/api/joke/"
    data_json = requests.get(url)
    data = data_json.json()
    witz = data[0]["text"]
    return JsonResponse({"witz":witz})
