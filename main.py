import requests
from bs4 import BeautifulSoup
import random
import time
import asyncio
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Proxy and headers
proxies = [
    "http://user:pass@proxy1:port",
    "http://user:pass@proxy2:port",
]

headers_list = [
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)..."},
]

def get(url):
    proxy = {"http": random.choice(proxies), "https": random.choice(proxies)}
    headers = random.choice(headers_list)
    try:
        r = requests.get(url, headers=headers, proxies=proxy, timeout=10)
        time.sleep(random.uniform(1, 2))
        return r
    except:
        return None

# Template scraper
def generic_scraper(config, keyword, page=1):
    url = config['url'].format(keyword=keyword, page=page)
    r = get(url)
    if not r: return []
    soup = BeautifulSoup(r.text, 'html.parser')
    results = []
    for vid in soup.select(config['selector']):
        try:
            title = vid.select_one(config['title']).text.strip()
            link = config['base'] + vid.select_one(config['link']).get('href')
            thumb = vid.select_one(config['thumb']).get('src')
            results.append({'title': title, 'link': link, 'thumb': thumb, 'source': config['name']})
        except:
            continue
    return results

# Scraper config
scraper_configs = [
    {
        'name': 'Redtube',
        'url': 'https://www.redtube.com/?search={keyword}&page={page}',
        'selector': '.video',
        'title': '.video-title',
        'link': 'a',
        'thumb': 'img',
        'base': 'https://www.redtube.com'
    },
    # Add more sites here...
]

# Async scrape
async def scrape_all(keyword):
    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(None, generic_scraper, config, keyword) for config in scraper_configs
    ]
    results = await asyncio.gather(*tasks)
    merged = [item for sublist in results for item in sublist]
    return merged

# API endpoint
@app.get("/search")
async def search_all(keyword: str = Query(...)):
    data = await scrape_all(keyword)
    return {"results": data}
