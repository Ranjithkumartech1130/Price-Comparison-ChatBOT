import requests
from bs4 import BeautifulSoup
import random
import urllib.parse

def get_headers():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ]
    return {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "en-US,en;q=0.9",
    }

def scrape_ebay(query):
    try:
        url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}"
        print(f"Scraping URL: {url}")
        response = requests.get(url, headers=get_headers())
        print(f"Response Status: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check if we are blocked
        page_title = soup.title.string if soup.title else "No Title"
        print(f"Page Title: {page_title}")

        items = []
        listings = soup.select('.s-item')
        print(f"Found {len(listings)} raw items")
        
        for item in listings[:8]:
            try:
                title = item.select_one('.s-item__title')
                price = item.select_one('.s-item__price')
                link = item.select_one('.s-item__link')
                
                if not (title and price and link):
                    continue

                title_text = title.text
                price_text = price.text
                link_href = link['href']
                
                # Filter out "Shop on eBay" dummy item
                if "Shop on eBay" in title_text or "New Listing" in title_text:
                    continue
                    
                items.append({
                    "source": "eBay",
                    "title": title_text,
                    "price": price_text,
                    "link": link_href
                })
            except Exception as e:
                # print(f"Error parsing item: {e}") 
                continue
        
        return items
    except Exception as e:
        print(f"Error scraping eBay: {e}")
        return []

def scrape_amazon_demo(query):
    pass

def custom_scraper(query):
    results = scrape_ebay(query)
    
    # If scraping failed or returned 0 items (common due to bot protection), 
    # we return mock data so the USER can still verify the UI and logic.
    if not results:
        print("Scraping returned 0 results. generating mock data for demo.")
        quoted_query = urllib.parse.quote(query)
        return [
            {
                "source": "eBay (Demo/Fallback)",
                "title": f"New {query} - High Performance",
                "price": "$199.99",
                "link": f"https://www.ebay.com/sch/i.html?_nkw={quoted_query}"
            },
            {
                "source": "Amazon (Demo/Fallback)",
                "title": f"{query} Pro Edition",
                "price": "$249.99",
                "link": f"https://www.amazon.com/s?k={quoted_query}"
            },
             {
                "source": "BestBuy (Demo/Fallback)",
                "title": f"Refurbished {query}",
                "price": "$150.00",
                "link": f"https://www.bestbuy.com/site/searchpage.jsp?st={quoted_query}"
            }
        ]

    # Add simulated competitor for visual comparison if we have real results
    if results:
        base_price_str = results[0]['price'].replace('$', '').replace(',', '').strip()
        try:
            if 'to' in base_price_str:
                base_price = float(base_price_str.split('to')[0].strip())
            else:
                base_price = float(base_price_str)
            
            mock_price = round(base_price * (1 + (random.random() * 0.2 - 0.1)), 2)
            
            # Create a search link for the title
            quoted_title = urllib.parse.quote(results[0]['title'])
            
            results.append({
                "source": "Amazon (Simulated)",
                "title": results[0]['title'],
                "price": f"${mock_price}",
                "link": f"https://www.amazon.com/s?k={quoted_title}"
            })
        except:
            pass
            
    return results
