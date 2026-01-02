import requests
from bs4 import BeautifulSoup
import random

def get_headers():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    ]
    return {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "en-US,en;q=0.9",
    }

def scrape_google_shopping(query):
    try:
        url = f"https://www.google.com/search?tbm=shop&q={query.replace(' ', '+')}"
        print(f"Scraping: {url}")
        response = requests.get(url, headers=get_headers())
        
        if response.status_code != 200:
            print(f"Failed: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Google Shopping HTML structure is cryptic and changes often.
        # Common classes: .i0X6df (card), .tAxDx (title), .a8Pemb (price)
        # Let's try to find common patterns.
        
        items = []
        # Try generic container search
        # Usually items are in div with class 'sh-dgr__content' or similar in grid
        
        results = soup.select('.i0X6df') # Common container class
        if not results:
             results = soup.select('.sh-dgr__content')

        print(f"Found {len(results)} potential items")

        for res in results[:5]:
            try:
                title = res.select_one('.tAxDx') or res.select_one('h3')
                price = res.select_one('.a8Pemb') or res.select_one('.OFFNJ')
                vendor = res.select_one('.aULzUe') or res.select_one('.IuHnof')
                
                # Link is often messy /url?q=...
                link_tag = res.select_one('a')
                
                if title and price:
                    items.append({
                        "source": vendor.text if vendor else "Google Shopping",
                        "title": title.text,
                        "price": price.text,
                        "link": "https://www.google.com" + link_tag['href'] if link_tag else url
                    })
            except Exception as e:
                print(e)
                continue
                
        return items

    except Exception as e:
        print(f"Error: {e}")
        return []

print(scrape_google_shopping("iphone 15"))
