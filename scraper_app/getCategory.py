import asyncio
import json

import aiohttp
from bs4 import BeautifulSoup
import re
import time


category_urls = {
    "essential oils": "https://isomerdesign.com/PiHKAL/essentialOils.php?domain=tk",
    "peyote alkaloids": "https://isomerdesign.com/PiHKAL/peyote.php?domain=pk",
    "aryldiaenpines": "https://isomerdesign.com/PiHKAL/tableLandscape.php?domain=tk&property=aryldiazepine&sort=name",
    "arylcycloalkylamine": "https://isomerdesign.com/PiHKAL/tableLandscape.php?domain=tk&property=arylcycloalkylamine&sort=name",
    "cannabinodids": "https://isomerdesign.com/PiHKAL/tableLandscape.php?domain=tk&property=cannabinoid&sort=name",
    "fentanyls": "https://isomerdesign.com/PiHKAL/tableLandscape.php?domain=tk&property=fentanyl&sort=name",
    "Phenetylamine": [],
    "Shulgin_Index": []
}

assignedCategorys = {}

category_list = {}
category_list_with_ids = {}

find_id_regex = re.compile(r'&id=\d{1,5}')
just_id_regex = re.compile(r'\d{1,5}')

async def get_category(category_name, category_url, session): #this method scarpes every category except Phen.. and the Shulgin_Index
    result = []
    try:
        print(category_name + " aufgerufen")
        async with session.get(category_url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            links = soup.find_all('a') #find all links, because all substances that have the category are linked to
            for link in links:
                href = link.get('href')
                if href:
                    match = find_id_regex.search(href)
                    if match:
                        id = just_id_regex.search(match.group(0)).group(0)
                        category_list_with_ids[id] = [category_name]
                        category_list[href] = [category_name]
    except aiohttp.ClientError as e:
        print(f"Error for category '{category_name}': {e}")



async def get_all_parts_for_parts(session, chapter_path,category, subcategory):
    urls = []
    async with session.get(chapter_path) as response:
        html = await response.text()
        text = BeautifulSoup(html, "html.parser")
        part_element = text.find(id="part")
        options = part_element.find_all('option')
        values = [option['value'] for option in options]   #extract all the parts of the subcategory
        for part_value in values:
            part = f"&part={part_value}"
            part_path = chapter_path + part
            await create_category_list(session, part_path, category, subcategory) #now the link is completed and all categorys are there that are linked to that one substance
            urls.append(part_path)
        return urls

async def add_Phenetylamine_Urls(session):
    url_list = []
    category = "Phenethylamine"
    phenetylamine_url = "https://isomerdesign.com/PiHKAL/tablePEA.php?domain=tk"
    async with session.get(phenetylamine_url) as response:
        html = await response.text()
        text = BeautifulSoup(html, "html.parser")
        chapter = text.find(id="chapter")
        options = chapter.find_all('option') #
        values = [option['value'] for option in options] #this are the numbers or values, based on them are the next chapters entered
        subcategorys = [option.string for option in options]  #this are the names of the subcategorys
        i = 0
        for chapter_value in values:
            c = f"&chapter={chapter_value}"
            chapter_path = phenetylamine_url + c # default path for Phen.. + one value of the options
            urls = await get_all_parts_for_parts(session, chapter_path, category, subcategorys[i]) #extract substances from this sub_path, the names of the category and the sub
                                                                                                #category are passed in
            i+=1
            url_list += urls
        return url_list

async def create_category_list(session, part_path,category, subcategory):   #this method gets one page of substances
    async with session.get(part_path) as response:
        html = await response.text()
        text = BeautifulSoup(html, "html.parser")
        links = text.find_all('a')
        info = [category, subcategory] #combine the category and the subcategory in one array
        print(info)
        for link in links:
            href = link.get('href')
            if href:
                match = find_id_regex.search(href)
                if match:
                    id = just_id_regex.search(href).group(0)
                    category_list_with_ids[id] = info
                    category_list[href] = info

async def get_all_parts_for_table(session, chapter_path, category, subcategory):
    urls = []

    async with session.get(chapter_path) as response:
        html = await response.text()
        text = BeautifulSoup(html, "html.parser")
        part_element = text.find(id="page")
        options = part_element.find_all('option')
        values = [option['value'] for option in options]
        for part_value in values:
            part = f"&page={part_value}"
            part_path = chapter_path + part
            await create_category_list(session, part_path, category, subcategory)
            urls.append(part_path)
        return urls
async def add_ShulginIndex_Urls(session):
    url_list = []
    category = "The Shulgin Index"
    root_url = "https://isomerdesign.com/PiHKAL/tableSI.php?domain=tk"
    async with session.get(root_url) as response:
        html = await response.text()
        text = BeautifulSoup(html, "html.parser")
        chapter = text.find(id="table")
        options = chapter.find_all('option')
        values = [option['value'] for option in options]
        subcategorys = [option.string for option in options]
        i = 0
        for chapter_value in values:
            c = f"&table={chapter_value}"  # shulgin index does hava a other url system then Phent...(tabels instead of chapter, page instead of parts
            chapter_path = root_url + c
            urls = await get_all_parts_for_table(session, chapter_path, category, subcategorys[i])
            i+=1
            url_list += urls
        return url_list

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [
            get_category(category_name=name, category_url=url, session=session)
            for name, url in category_urls.items() if name != "Phenetylamine" and name != "Shulgin_Index"
        ] #scrape every category exept Ph.. and Shulgin... because they have a different structure
        await asyncio.gather(*tasks)
        urls = await add_Phenetylamine_Urls(session)
        category_urls["Phenetylamine"] = urls
        urls = await add_ShulginIndex_Urls(session)
        category_urls["Shulgin_Index"] = urls

        count = 0


def getCategorys():
    start = time.time()
    asyncio.run(main()) #start the programm that scrapes all the categorys and looks which substances are listed there
    print(f"Runtime:  {int(time.time() - start)}")
    print(str(len(category_list.keys())) + " ids found")
    with open("cateogry_json_file.json","w") as file:
        json.dump(category_list, file)

    print(str(len(category_list_with_ids.keys())) + " ids found")
    with open("cateogry_id_json_file.json", "w") as file:
        json.dump(category_list_with_ids, file)
    return category_list_with_ids

