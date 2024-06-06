
import asyncio
import aiohttp
import json
import os
import time
from bs4 import BeautifulSoup
import re
from .getCategory import getCategorys


findable = []
newOnes_bySMILES = []


async def test_if_url_is_accesable(session, url, index):
    try:
        async with session.get(url) as response:
            if response.status != 200:
                return True
            findable.append(str(index))
            print(url +" added to findable")
            return True
    except:
        print("url not accessable")



async def look():
    urls = [f"https://isomerdesign.com/pihkal/explore/{i}" for i in
            range(1, 16000)]
    try:
        timeout = aiohttp.ClientTimeout(total=None, connect=None, sock_connect=None, sock_read=60)
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20), timeout=timeout) as session:
            tasks = [test_if_url_is_accesable(session, url, index) for index, url in enumerate(urls, 1)]
            result = await asyncio.gather(*tasks)
    except:
        print("skipped")

def get_urls_of_new_substances():
    asyncio.run(look())
    newOnes = []
    old_data_folder = os.listdir("./response_data")
    for suffix in findable:
        to_comp = "substance_" + suffix + ".json"
        if to_comp not in old_data_folder:
            newUrl = "https://isomerdesign.com/pihkal/explore/" + suffix
            newOnes.append(newUrl)
    print("new urls saved in list")
    return newOnes
    


async def fetch_url(session, url, folder,categorys):

    try:  # for the case that the uls isnt accessible
        async with session.get(url) as response:
            if response.status != 200:
                return True
            html = await response.text()  # wait until the server responses
            # parse to process data better
            data = BeautifulSoup(html, "html.parser")

            # extrac informations from data
            id_regex = re.compile(r"(.*)id=(\d{1,5})")
            index = id_regex.search(url).group(2)
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

            #category
            # look, if the index is known in categorys
            for dictionary, list_of_indexes in categorys.items():
                if index in list_of_indexes:
                    category = str(dictionary)
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
            inchl = match.group(1)
            # inchl_key
            inchl_key = clippable[data_quantity - 2].text
            #smiles
            smiles = data.find(id="smiles").text
            global newOnes_bySMILES
            newOnes_bySMILES.append(smiles)
            print("newJsonFile")
            data_dict = {
                "names": names,
                "iupac_name": iupac,
                "category": category,
                "index": index,
                "formular": formular,
                "molecular_weight": molecular_weight,
                "inChl": inchl,
                "InChl_Key": inchl_key,
                "SMILES": smiles
            }
            # open the json file

            filename = os.path.join(folder, f"substance_{index}.json")
            # Den Daten in eine JSON-Datei schreiben
            with open(filename, "w") as file:
                json.dump(data_dict, file, indent=4)
            print("newJsonFile: "+filename+" added to folder")
            return True
    except Exception as e:
        print(f"Fehler beim Abrufen der URL {url}: {e}")
        return True

async def get_responses(urls,categorys):
    folder = "response_data"  # Der Zielordner, in dem die JSON-Dateien gespeichert werden sollen
    os.makedirs(folder, exist_ok=True)  # Erstellen Sie den Ordner, falls er nicht existiert
      # the list with all urls is created
    
    try:
        timeout = aiohttp.ClientTimeout(total=None, connect=None, sock_connect=None, sock_read=60) #total timelimit for the whole reques /
 # Timeout von 60 Sekunden für Socken lesen
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=100),timeout=timeout) as session: #to limit the requests in order to respekt the server """connector=aiohttp.TCPConnector(limit=10)"""
                # creates ClientSession-Object to manage the asynchron Communication; within the async with-block, get-requests are done; clears after himself when done
                tasks = [fetch_url(session, url, folder,categorys) for url in urls]  # create a list of tasks, where every item is a call of the fetch_url function
                responses = await asyncio.gather(*tasks)  # wait until all tasks(calls of the fetch_url-function) came to a result
    except aiohttp.ClientConnectionError:
        print("Conntection was dropped before finishing")
    except aiohttp.ServerTimeoutError:
        print("Timeouterror")

def getNewSubstances():
    urls = get_urls_of_new_substances()
    print("all new urls loaded")
    with open("categorys.json", 'r') as f: 
        categorys = json.load(f)
    #categorys = getCategorys() # look for categorys and connected ids on your own  #    
    # #load the categorys from external file in order to improve the speed, categorys are NOT!!! loaded in in this run
    asyncio.run(get_responses(urls, categorys))
    print("newOnesReturnedFromgetNewSubstance: ")
    for smile in newOnes_bySMILES:
        print(smile)
    return newOnes_bySMILES
