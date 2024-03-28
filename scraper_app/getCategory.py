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
find_id_regex = re.compile(r'&id=\d{1,5}')
just_id_regex = re.compile(r'\d{1,5}')

async def get_category(category_name, category_url, session):
    result = []
    try:
        async with session.get(category_url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            links = soup.find_all('a')
            for link in links:
                href = link.get('href')
                if href:
                    match = find_id_regex.search(href)
                    if match:
                        id = just_id_regex.search(href)
                        result.append(int(id.group()))
    except aiohttp.ClientError as e:
        print(f"Error for category '{category_name}': {e}")
    if category_name != "Phenetylamine" and category_name != "Shulgin_Index":
        assignedCategorys[category_name] = result
    else:
        if category_name not in assignedCategorys.keys():
            assignedCategorys[category_name] = result
        else:
            assignedCategorys[category_name].extend(result)
    return category_name, result

async def get_all_parts_for_parts(session, chapter_path):
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
            urls.append(part_path)
        return urls

async def add_Phenetylamine_Urls(session):
    url_list = []
    phenetylamine_url = "https://isomerdesign.com/PiHKAL/tablePEA.php?domain=tk"
    async with session.get(phenetylamine_url) as response:
        html = await response.text()
        text = BeautifulSoup(html, "html.parser")
        chapter = text.find(id="chapter")
        options = chapter.find_all('option')
        values = [option['value'] for option in options]
        for chapter_value in values:
            c = f"&chapter={chapter_value}"
            chapter_path = phenetylamine_url + c
            urls = await get_all_parts_for_parts(session, chapter_path)
            url_list += urls
        return url_list


async def get_all_parts_for_table(session, chapter_path):
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
            urls.append(part_path)
        return urls
async def add_ShulginIndex_Urls(session):
    url_list = []
    root_url = "https://isomerdesign.com/PiHKAL/tableSI.php?domain=tk"
    async with session.get(root_url) as response:
        html = await response.text()
        text = BeautifulSoup(html, "html.parser")
        chapter = text.find(id="table")
        options = chapter.find_all('option')
        values = [option['value'] for option in options]
        for chapter_value in values:
            c = f"&table={chapter_value}"  # shulgin index does hava a other url system then Phent...(tabels instead of chapter, page instead of parts
            chapter_path = root_url + c
            urls = await get_all_parts_for_table(session, chapter_path)
            url_list += urls
        return url_list

async def main():
    async with aiohttp.ClientSession() as session:
        urls = await add_Phenetylamine_Urls(session)
        category_urls["Phenetylamine"] = urls
        urls = await add_ShulginIndex_Urls(session)
        category_urls["Shulgin_Index"] = urls
        tasks = [
            get_category(category_name=name, category_url=url, session=session)
            for name, url in category_urls.items() if name != "Phenetylamine" and name != "Shulgin_Index"
        ]
        tasks.extend(
            get_category(category_name="Phenetylamine", category_url=url, session=session)
            for url in category_urls["Phenetylamine"]
        )
        tasks.extend(
            get_category(category_name="Shulgin_Index", category_url=url, session=session)
            for url in category_urls["Shulgin_Index"]
        )
        results = await asyncio.gather(*tasks)
        count = 0
        for category, values in assignedCategorys.items():
            count += len(values)
            print(f"{category}: {len(values)}")
        print(f"{count} ids found")

def getCategorys():
    start = time.time()
    asyncio.run(main())
    print(f"Runtime:  {int(time.time() - start)}")
    return assignedCategorys

def create_category_json():
    data_dict = {}
    categorys_d = getCategorys()
    for dictionary, list in categorys_d.items():
        data_dict[dictionary] = list

    with open("categorys.json", "w") as file:
        json.dump(data_dict, file, indent=4)
