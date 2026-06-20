from server import fetch_and_remember_website, search_memory
import time

print("1. Activating Automated Web Scraper...")
# e are scraping an actual public webpage detailing Python's official documentation overview

test_url="https://www.python.org/doc/essays/"
print(f"Scraping {test_url} and saving to memory")
res=fetch_and_remember_website(test_url, "python_essays.md")
print(res)
print("\nWaiting a quick moment for database sync...")
time.sleep(1)
print("\n2. Testing Semantic Retrieval over the scraped internet data...")
# we search for "historical papers" or "design philosophy"
search_qry="history and design philosophy of programming"
print(f"searching memory for: '{search_qry}")
search_res=search_memory(search_qry)
print(search_res)