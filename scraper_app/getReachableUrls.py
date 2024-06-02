import asyncio
import aiohttp
import json
import os
import time
from bs4 import BeautifulSoup
import re
from periodictable import formula
from .getCategory import get_category
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors
from .models import Substances
from .getData import getData

changes_accoure = []

find_id_regex = re.compile(r'&id=\d{1,5}')
just_id_regex = re.compile(r'\d{1,5}')

previous_categorys = {}
gathered_substances = []
getDataObject = getData()


not_reachable = []
counter = 0


async def find_not_reachable_urls(session, url):
    global counter
    counter += 1
    try:
        if counter % 100 == 0:
            print(counter)
        async with session.head(url) as response:
            status_code = response.status
            if status_code >= 400:
                not_reachable.append(url)
            else:
                changes_accoure.append(url)
    except:
        print("couldnt make connection")
        not_reachable.append(url)


async def manage(urls): #here is tested if the urls that were previous not accessable are stil like that
   print(f"Length of urls: {len(urls)}")
   timeout = aiohttp.ClientTimeout(total=None, connect=None, sock_connect=None, sock_read=60)
   async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=30), timeout=timeout) as session:
        tasks = [find_not_reachable_urls(session, url) for url in urls]
        await asyncio.gather(*tasks)


def getReachableUrls():
    counter = 0
    try:
        with open("not_reachable_urls.json", "r") as json_file:
            file = json.load(json_file)
        previous_not_reachable = file["not_reachable"]
        
        print("not_reachable loaded")
        with open("category_json_file.json","r") as file:
            global previous_categorys
            previous_categorys = json.load(file)
            print("categorys loaded")
        asyncio.run(manage(previous_not_reachable))
 
    except:
        print("previous not reachable urls couldnt be loaded")
        urls = [f"https://isomerdesign.com/pihkal/explore/{i}" for i in range(1, 17000)]
        asyncio.run(manage(urls))
        print("url-accessability determined")
    data = {
        "not_reachable": not_reachable
    }
    with open("not_reachable_urls.json", "w") as file: #the json file that contains all not reachable urls is updated
        json.dump(data, file)
    data = {
        "new_ones": changes_accoure
    }
    print(str(changes_accoure))
    if changes_accoure is not None:
        print("changes_accoure")
        getDataObject.start(changes_accoure)
    return changes_accoure

