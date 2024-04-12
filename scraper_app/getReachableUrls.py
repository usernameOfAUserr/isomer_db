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

changes_accoure = []

find_id_regex = re.compile(r'&id=\d{1,5}')
just_id_regex = re.compile(r'\d{1,5}')


async def fetch_url(session, url, folder, categorys):
    match = find_id_regex.search(url)
    if match:
        index = int(just_id_regex.search(url).group(0))
    try:  # for the case that the uls isnt accessible
        async with session.get(url) as response:
            if response.status != 200:
                return True
            if index % 100 == 0:
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
                names = ""
                names_div = pDesc_divs[0]
                """text = names_div.text
                if names_regex.search(text) is not None:"""
                childs = names_div.find_all(class_="clippable")
                for child in childs:
                    if child is not childs[0]:
                        names += f" ; {child.text}"
                    else:
                        names += f"{child.text}"

                # iupac
                iupac = ""
                iupac_div = pDesc_divs[1]
                childs = iupac_div.find_all(class_="clippable")
                for child in childs:
                    if child is not childs[0]:
                        iupac += f" ; {child.text}"
                    else:
                        iupac += f"{child.text}"
            except:
                print(f"error by url {url}, data_quantity: {data_quantity}")
                return True

            # index & category
            category = "data not stored"
            # substance_index = index

            # category
            # look, if the index is known in categorys
            for dictionary, list_of_indexes in categorys.items():
                if index in list_of_indexes:
                    category = str(dictionary)
                else:
                    try:
                    # search for tag in the data that reviels the category
                        tags = data.find_all(class_="sLabel")
                        for tag in tags:
                            if tag.text == "Tags":
                                right_div = tag.parent
                                text = right_div.text.strip()
                                category = text.replace("Tags", "").strip()
                    except:
                        pass
            # formular
            formular = clippable[data_quantity - 5].text

            # molecular_weight
            molecular_weight = clippable[data_quantity - 4].text
            molecular_weight = float(molecular_weight)

            # inChl
            InChl_regex = re.compile(r"InChI=(.*)")
            match = InChl_regex.search(clippable[data_quantity - 3].text)
            inchl = match.group(1)
            # inchl_key
            inchl_key = clippable[data_quantity - 2].text
            smiles = data.find(id="smiles").text

            # validation
            molecule = Chem.MolFromSmiles(smiles)
            canonical_smiles = Chem.MolToSmiles(molecule)
            weight_chem = Descriptors.MolWt(molecule)
            formula_chem = rdMolDescriptors.CalcMolFormula(molecule)
            validation_message = ""
            if molecular_weight != round(weight_chem, 2):
                validation_message += f"m_weight unsave, calculated({weight_chem})"
            if formula_chem != formular:
                validation_message += f"formular unsave, calculated({formula_chem})"
            data_dict = {
                "names": names,
                "iupac_name": iupac,
                "category": category,
                "index": index,
                "formular": formular,
                "molecular_weight": molecular_weight,
                "inChl": inchl,
                "InChl_Key": inchl_key,
                "SMILES": canonical_smiles,
                "url": url,
                "validation": validation_message
            }
            # open the json file

            filename = os.path.join(folder, f"substance_{index}.json")
            # Den Daten in eine JSON-Datei schreiben
            with open(filename, "w") as file:
                json.dump(data_dict, file, indent=4)
            return True
    except Exception as e:
        print(f"Fehler beim Abrufen der URL {url}: {e}")
        return True


async def get_responses(categorys, urls):
    print(f"urls to insert: {urls}")
    folder = "new_ones"  # Der Zielordner, in dem die JSON-Dateien gespeichert werden sollen
    os.makedirs(folder, exist_ok=True)  # Erstellen Sie den Ordner, falls er nicht existiert
    # the list with all urls is created
    try:
        timeout = aiohttp.ClientTimeout(total=None, connect=None, sock_connect=None,
                                        # total timelimit for the whole reques /

                                        sock_read=60)  # Timeout von 60 Sekunden für Socken lesen
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20),
                                         timeout=timeout) as session:  # to limit the requests in order to respekt the server """connector=aiohttp.TCPConnector(limit=10)"""
            # creates ClientSession-Object to manage the asynchron Communication; within the async with-block, get-requests are done; clears after himself when done
            tasks = [fetch_url(session, url, folder, categorys) for url in
                     urls]  # create a list of tasks, where every item is a call of the fetch_url function
            responses = await asyncio.gather(
                *tasks)  # wait until all tasks(calls of the fetch_url-function) came to a result
    except aiohttp.ClientConnectionError:
        print("Conntection was dropped before finishing")
    except aiohttp.ServerTimeoutError:
        print("Timeouterror")


def start():
    print("begining insertin into json files")
    # categorys = getCategorys() # look for categorys and connected ids on your own  #
    try:
        with open("categorys.json", 'r') as f:
            categorys = json.load(f)
        asyncio.run(get_responses(categorys, changes_accoure))
    except:
        categorys = get_category()
        print("I had to look for changes in categorys as well :(\n")
    # #load the categorys from external file in order to improve the speed, categorys are NOT!!! loaded in in this run
        asyncio.run(get_responses(categorys, changes_accoure))

    ####################################################################################


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


async def manage(urls):
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
    print("not_reachable loaded")
    asyncio.run(manage(previous_not_reachable))
    """
    except:
        print("previous not reachable urls couldnt be loaded")
        urls = [f"https://isomerdesign.com/PiHKAL/explore.php?domain=pk&id={i}" for i in range(1300, 16000)]
        asyncio.run(manage(urls))
        print("url-accessability determined")
        """
    data = {
        "not_reachable": not_reachable
    }
    with open("not_reachable_urls.json", "w") as file:
        json.dump(data, file)
    data = {
        "new_ones": changes_accoure
    }
    with open("new_ones.json", "w") as file:
        json.dump(data, file)
    if changes_accoure is not None:
        print(changes_accoure)
        start()
    return changes_accoure