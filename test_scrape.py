from backend.scraper import custom_scraper

print("Testing Scraper...")
results = custom_scraper("laptop")
print(f"Found {len(results)} items.")
for item in results:
    print(item)
