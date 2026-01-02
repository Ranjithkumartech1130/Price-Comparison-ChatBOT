import requests
from bs4 import BeautifulSoup
import random

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

def scrape_bing(query):
    url = f"https://www.bing.com/shop?q={query.replace(' ', '+')}"
    print(f"Scraping {url}")
    try:
        response = requests.get(url, headers=get_headers())
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Bing classes: .br-item (card), .br-tit (title), .br-price (price), .br-sname (store)
        items = []
        results = soup.select('.br-item')
        print(f"Found {len(results)} items")
        
        for res in results[:5]:
            title = res.select_one('.br-tit')
            price = res.select_one('.br-price')
            store = res.select_one('.br-sname') or res.select_one('.br-seller')
            
            if title and price:
                items.append({
                    "source": store.text if store else "Bing Shopping",
                    "title": title.text,
                    "price": price.text,
                    "link": url # The real links are often redirects
                })
        return items
    except Exception as e:
        print(e)
        return []

print(scrape_bing("laptop"))
