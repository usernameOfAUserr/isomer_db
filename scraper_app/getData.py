import asyncio
import aiohttp
import json
import os
import time
from bs4 import BeautifulSoup
import re
from periodictable import formula
from .getCategory import getCategorys
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors
from .models import Substances
from .Store import Store

class getData:
    Storer = Store()
    progress = 0
    gatherd_substances = []
    Substances = Substances.objects.all()
    find_id_regex = re.compile(r'&id=\d{1,5}')
    just_id_regex = re.compile(r'\d{1,5}')
    categorys = {}
    def __init__(self) -> None:
        pass

   
    def getProgress(self):
        return self.progress
    

    async def fetch_url(self, session, url, index):

        try:  # for the case that the uls isnt accessible
            async with session.get(url) as response:
                if response.status != 200:
                    return True 
        
                if index %100 == 0:
                    self.progress = index / 150
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
                category = []
                # substance_index = index

                #category
                # look, if the index is known in categorys
                id_string_match = self.find_id_regex.search(url)
                if id_string_match:
                    id = self.just_id_regex.search(id_string_match.group()).group()
                if id in self.categorys.keys():
                    category =self.categorys[id]
                    """
                        needed_format_of_url = "https://isomerdesign.com/PiHKAL/search.php?domain=tk&id="+str(id)
                        if needed_format_of_url in self.categorys.keys():
                            category.append(self.categorys[needed_format_of_url])
                            print(self.categorys[needed_format_of_url])
                         elif url in self.categorys.keys():
                            category.append(self.categorys[url])
                            print(self.categorys[url])
                    """
                else:
            # search for tag in the data that reviels the categorypyto
                    tags = data.find_all(class_="sLabel")
                    for tag in tags:
                        if tag.text == "Tags":
                            right_div = tag.parent
                            text = right_div.text.strip()
                            category_found = text.replace("Tags", "").strip()
                            category = category_found
                if len(category) == 0:
                    category.append("unknown")
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
                if molecular_weight < round(weight_chem,2) - 0.1 or molecular_weight > round(weight_chem, 2)+ 0.1:
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
                self.gatherd_substances.append(data_dict)
                
                return True
        except Exception as e:
            print(f"Fehler beim Abrufen der URL {url}: {e}")
            return True



    async def get_responses(self, urls):

        folder = "response_data"  # Der Zielordner, in dem die JSON-Dateien gespeichert werden sollen
        os.makedirs(folder, exist_ok=True)  # Erstellen Sie den Ordner, falls er nicht existiert
        # the list with all urls is created
        try:
            timeout = aiohttp.ClientTimeout(total=None, connect=None, sock_connect=None, #total timelimit for the whole reques /

                                            sock_read=60)  # Timeout von 60 Sekunden für Socken lesen
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=40),timeout=timeout) as session: #to limit the requests in order to respekt the server """connector=aiohttp.TCPConnector(limit=10)"""
                    # creates ClientSession-Object to manage the asynchron Communication; within the async with-block, get-requests are done; clears after himself when done
                    tasks = [self.fetch_url(session, url, index) for index, url in
                            enumerate(urls, 1)]  # create a list of tasks, where every item is a call of the fetch_url function
                    responses = await asyncio.gather(
                        *tasks)  # wait until all tasks(calls of the fetch_url-function) came to a result
        except aiohttp.ClientConnectionError:
            print("Conntection was dropped before finishing")
        except aiohttp.ServerTimeoutError:
            print("Timeouterror")

    def start(self):
        self.progress = 0
        urls = [f"https://isomerdesign.com/PiHKAL/explore.php?domain=pk&id={i}" for i in range(1, 16000)]
        reuse_old_categorys = True
        if reuse_old_categorys:
            with open("cateogry_id_json_file.json", 'r') as f: 
                self.categorys = json.load(f)
        else:
            self.categorys = getCategorys() 
        # #load the categorys from external file in order to improve the speed, categorys are NOT!!! loaded in in this run
        asyncio.run(self.get_responses(urls))
        self.Storer.Substances(self.gatherd_substances)

    