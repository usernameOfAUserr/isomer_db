
cd C:\Users\User\PycharmProjects\web_scraper
pip install asyncio
pip install aiohttp
pip install bs4
pip install periodictable
pip install rdkit
pip install shutil
echo Starting Django development server...
start cmd /k "python manage.py runserver" > logging_from_bat.txt
echo Waiting for the server to start..."
ping 127.0.0.1 -n 5 > nul
echo Opening browser..."
start http://127.0.0.1:8000/webscraper
