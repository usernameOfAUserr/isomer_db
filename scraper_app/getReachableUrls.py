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

changes_accoure = []

find_id_regex = re.compile(r'&id=\d{1,5}')
just_id_regex = re.compile(r'\d{1,5}')

previous_categorys = {}
gathered_substances = []
async def fetch_url(session, url):

    try:  # for the case that the uls isnt accessible
        async with session.get(url) as response:
            if response.status != 200:
                return True
            
            print(f"done for {url}")
            
            html = await response.text()  # wait until the server responses
            # parse to process data better
            data = BeautifulSoup(html, "html.parser")

            # extrac informations from data

            clippable = data.find_all(class_="clippable")
            data_quantity = len(clippable)

            # names
            try:
                names_regex = re.compile(r"Names")
                pDesc_divs = data.find_all(class_="pDesc")  # here are the names stored(normal+iupac), the parent div
                names = []
                names_div = pDesc_divs[0]
                """text = names_div.text
                if names_regex.search(text) is not None:"""
                childs = names_div.find_all(class_="clippable")
                for child in childs:
                    names.append(child.text)

                # iupac
                iupac = []
                iupac_div = pDesc_divs[1]
                childs = iupac_div.find_all(class_="clippable")
                for child in childs:
                    iupac.append(child.text)
            except:
                print(f"error by url {url}, data_quantity: {data_quantity}")
                return True

            # index & category
            category = ["data not stored"]
            # substance_index = index

            #category
            # look, if the index is known in categorys
            if url in previous_categorys.keys():
                category = previous_categorys[url]
            else:
        # search for tag in the data that reviels the category
                tags = data.find_all(class_="sLabel")
                for tag in tags:
                    if tag.text == "Tags":
                        right_div = tag.parent
                        text = right_div.text.strip()
                        category = text.replace("Tags", "").strip()
            # formular
            formular = clippable[data_quantity - 5].text

            # molecular_weight
            molecular_weight = clippable[data_quantity - 4].text
            molecular_weight = float(molecular_weight)

            # inChl
            InChl_regex = re.compile(r"InChI=(.*)")
            match = InChl_regex.search(clippable[data_quantity - 3].text)
            inchi = match.group(1)
            # inchl_key
            inchi_key = clippable[data_quantity - 2].text
            smiles = data.find(id="smiles").text

            #validation
            is_valid = True
            molecule = Chem.MolFromSmiles(smiles)
            canonical_smiles = Chem.MolToSmiles(molecule)
            weight_chem = Descriptors.MolWt(molecule) 
            formula_chem = rdMolDescriptors.CalcMolFormula(molecule)
            if molecular_weight != round(weight_chem,2):
                is_valid = False
            if formula_chem != formular:
                is_valid = False

            data_dict = {
                "smiles": canonical_smiles,
                "names": names,
                "iupac_name": iupac,
                "formular": formular,
                "inchi": inchi,
                "inchi_key": inchi_key,
                "molecular_mass": molecular_weight,
                "cas_num": 0,
                "category": category,
                "source_name": "PIHKAL",
                "source_url": url,
                "valid": is_valid,
                "deleted": False,
                "version": 0.0,
                "details": [],
            }
            global gathered_substances
            gathered_substances.append(data_dict)
            
            return True
    except Exception as e:
        print(f"Fehler beim Abrufen der URL {url}: {e}")
        return True


async def get_responses(urls):
    print(f"urls to insert: {urls}")
    try:
        timeout = aiohttp.ClientTimeout(total=None, connect=None, sock_connect=None,
                                        # total timelimit for the whole reques /

                                        sock_read=60)  # Timeout von 60 Sekunden für Socken lesen
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20),
                                         timeout=timeout) as session:  # to limit the requests in order to respekt the server """connector=aiohttp.TCPConnector(limit=10)"""
            # creates ClientSession-Object to manage the asynchron Communication; within the async with-block, get-requests are done; clears after himself when done
            tasks = [fetch_url(session, url) for url in
                     urls]  # create a list of tasks, where every item is a call of the fetch_url function
            responses = await asyncio.gather(
                *tasks)  # wait until all tasks(calls of the fetch_url-function) came to a result
    except aiohttp.ClientConnectionError:
        print("Conntection was dropped before finishing")
    except aiohttp.ServerTimeoutError:
        print("Timeouterror")




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
        results = await asyncio.gather(*tasks)


def getReachableUrls():
    counter = 0
    with open("not_reachable_urls.json", "r") as json_file:
        file = json.load(json_file)
    previous_not_reachable = file["not_reachable"]
    for url in previous_not_reachable:
        print(url+"\n")
    print("not_reachable loaded")
    with open("category_json_file.json","r") as file:
        global previous_categorys
        previous_categorys = json.load(file)
        print("categorys loaded")
    asyncio.run(manage(previous_not_reachable))
    """
    except:
        print("previous not reachable urls couldnt be loaded")
        urls = [f"https://isomerdesign.com/PiHKAL/explore.php?domain=pk&id={i}" for i in range(1, 16000)]
        asyncio.run(manage(urls))
        print("url-accessability determined")
        """
    data = {
        "not_reachable": not_reachable
    }
    with open("not_reachable_urls.json", "w") as file: #the json file that contains all not reachable urls is updated
        json.dump(data, file)
    data = {
        "new_ones": changes_accoure
    }
    if changes_accoure is not None:
        print(changes_accoure)
        asyncio.run(get_responses(changes_accoure))
        store_in_db()
    return changes_accoure


def store_in_db():
    for substance in gathered_substances:
        data_dict = substance
        url = substance['source_url']
        existing_object = Substances.objects.filter(source_name="PIHKAL", source_url=url)
        if existing_object:
            existing_object.delete()
            print(str(substance) +" removed form db")
        new_object = Substances.objects.create(
            smiles=data_dict['smiles'],
            names=data_dict['names'],
            iupac_name=data_dict['iupac_name'],
            formular=data_dict['formular'],
            inchi=data_dict['inchi'],
            inchi_key=data_dict['inchi_key'],
            molecular_mass=data_dict['molecular_mass'],
            cas_num=data_dict['cas_num'],
            category=data_dict['category'],
            source_name=data_dict['source_name'],
            source_url=data_dict['source_url'],
            valid=data_dict['valid'],
            deleted=data_dict['deleted'],
            version=data_dict['version'],
            details=data_dict['details']
        )
        print(str(substance['names']) +" added to db")