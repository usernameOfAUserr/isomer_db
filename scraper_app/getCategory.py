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

find_id_regex = re.compile(r'&id=\d{1,5}')
just_id_regex = re.compile(r'\d{1,5}')

async def get_category(category_name, category_url, session):
    result = []
    try:
        print(category_name + " aufgerufen")
        async with session.get(category_url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            links = soup.find_all('a')
            for link in links:
                href = link.get('href')
                if href:
                    match = find_id_regex.search(href)
                    if match:

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
        values = [option['value'] for option in options]
        for part_value in values:
            part = f"&part={part_value}"
            part_path = chapter_path + part
            await create_category_list(session,part_path, category,subcategory)
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
        options = chapter.find_all('option')
        values = [option['value'] for option in options]
        subcategorys = [option.string for option in options]
        i = 0
        for chapter_value in values:
            c = f"&chapter={chapter_value}"
            chapter_path = phenetylamine_url + c
            urls = await get_all_parts_for_parts(session, chapter_path, category, subcategorys[i])
            i+=1
            url_list += urls
        return url_list

async def create_category_list(session, part_path,category, subcategory):
    async with session.get(part_path) as response:
        html = await response.text()
        text = BeautifulSoup(html, "html.parser")
        links = text.find_all('a')
        info = [category, subcategory]
        print(info)
        for link in links:
            href = link.get('href')
            if href:
                match = find_id_regex.search(href)
                if match:
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
        ]
        await asyncio.gather(*tasks)
        urls = await add_Phenetylamine_Urls(session)
        category_urls["Phenetylamine"] = urls
        urls = await add_ShulginIndex_Urls(session)
        category_urls["Shulgin_Index"] = urls

        count = 0


def getCategorys():
    start = time.time()
    asyncio.run(main())
    print(f"Runtime:  {int(time.time() - start)}")
    print(str(len(category_list.keys())) + " ids found")
    with open("category_json_file.json","w") as file:
        json.dump(category_list, file)
    return category_list
