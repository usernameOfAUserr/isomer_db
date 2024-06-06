import asyncio
import aiohttp
import json
import os
import time
from bs4 import BeautifulSoup
import re
from periodictable import formula
from .new_getCategory import getCategorys
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
                
                all_clippable = data.findAll(class_='clippable')
                number_of_clippable = len(all_clippable)

                # names and iupac, can be tricky because sometimes, there are no names as well as no iupac, so it has to be calculated what exactly is there
                try:
                    name_list = data.findAll('ul', class_='name-list')
                    names = []
                    iupac = []
                    # names
                    if len(name_list) == 2:
                        for name in name_list[0]:
                            if name.name == "li":
                                names.append(name.text.strip())
                        # iupac
                        for name in name_list[1]:
                            if name.name == "li":
                                iupac.append(name.text.strip())
                    elif len(name_list) == 1:
                        # now, I calculate the position of iupac and names, in addition regex to pin down where the iupac begins
                        parent_of_name_list = name_list[0].find_parent().find_parent()
                        child_elements = parent_of_name_list.children
                        just_iupac_exists = False
                        for child in child_elements:
                            if child.text == "IUPAC names" or child.text == "IUPAC name":
                                just_iupac_exists = True
                                names.append("Unknown")
                                for name in name_list[0]:
                                    if name.name == "li":
                                        iupac.append(name.text.strip())
                        if not just_iupac_exists:
                            iupac.append("Unknown")
                            for name in name_list[0]:
                                if name.name == "li":
                                    names.append(name.text.strip())
                    else:
                        iupac.append("Unknown")
                        names.append("Unknown")
         
                except:
                    print(f"error by url {url}, data_quantity: {number_of_clippable}")


                # index & category
                category = []
                # substance_index = index

                # category
                # look, if the index is known in categorys
                id = data.find(id='substance-id').text
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
                if len(category) == 0:
                    category.append("unknown")
                # formular
                all_clippable = data.findAll(class_='clippable')
                number_of_clippable = len(data.findAll(class_='clippable'))
                formular = all_clippable[number_of_clippable-5].text
                # molecular_weight
                molecular_weight = all_clippable[number_of_clippable-4].text
                molecular_weight = float(molecular_weight)
                # inChl
                InChl_regex = re.compile(r"InChI=(.*)")
                match = InChl_regex.search(all_clippable[number_of_clippable-3].text)
                inchi = match.group(1)
                # inchl_key
                inchi_key = all_clippable[number_of_clippable-2].text
                #smiles
                smiles = data.find(id='smiles').text
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
                    "iupac_names": iupac,
                    "formula": formular,
                    "inchi": inchi,
                    "inchi_key": inchi_key,
                    "molecular_mass": molecular_weight,
                    "cas_num": 0,
                    "categories": category,
                    "source": {"name": "PIHKAL", "url": url},
                    "validated": is_valid,
                    "deleted": False,
                    "version": "0.0",
                    "details": {},
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
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=30),timeout=timeout) as session: #to limit the requests in order to respekt the server """connector=aiohttp.TCPConnector(limit=10)"""
                    # creates ClientSession-Object to manage the asynchron Communication; within the async with-block, get-requests are done; clears after himself when done
                    tasks = [self.fetch_url(session, url, index) for index, url in
                            enumerate(urls, 1)]  # create a list of tasks, where every item is a call of the fetch_url function
                    responses = await asyncio.gather(
                        *tasks)  # wait until all tasks(calls of the fetch_url-function) came to a result
        except aiohttp.ClientConnectionError:
            print("Conntection was dropped before finishing")
        except aiohttp.ServerTimeoutError:
            print("Timeouterror")

    def start(self, urls):
        self.progress = 0
        if urls is None:
            urls = [f"https://isomerdesign.com/pihkal/explore/{i}" for i in range(1, 17000)]
        reuse_old_categorys = True
        if reuse_old_categorys:
            with open("cateogry_id_json_file.json", 'r') as f: 
                self.categorys = json.load(f)
        else:
            self.categorys = getCategorys() 
        # #load the categorys from external file in order to improve the speed, categorys are NOT!!! loaded in in this run
        asyncio.run(self.get_responses(urls))
        self.Storer.Substances(self.gatherd_substances)

    