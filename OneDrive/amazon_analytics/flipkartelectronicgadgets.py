import random
import time
import requests
from bs4 import BeautifulSoup

class FlipkartScraper:
    def __init__(self, product, pages):
        self.product = product.replace(" ", "+")  # Replace spaces with '+'
        self.pages = pages
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/68.0',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'
        ]
    
    def scrape(self):
        for page_num in range(1, int(self.pages) + 1):
            print(f"Accessing Flipkart page {page_num}")
            my_url = f"https://www.flipkart.com/search?q={self.product}&page={page_num}"
            
            # Randomize User-Agent
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }

            try:
                response = requests.get(my_url, headers=headers)
                response.raise_for_status()  # Raise an error for 4xx/5xx responses
                page_html = response.text
            except Exception as e:
                print(f"Failed to retrieve Flipkart page {page_num}. Error: {e}")
                continue

            page_soup = BeautifulSoup(page_html, "html.parser")
            containers = page_soup.findAll("a", {"class": "CGtC98"})

            for container in containers:
                product_data = self.extract_product_data(container)
                if product_data:
                    self.print_product_data(*product_data)

            print(f"Flipkart page {page_num} finished\n")
            time.sleep(random.uniform(3, 5))  # Increase delay to avoid too many requests

    def extract_product_data(self, container):
        try:
            link = container['href']
            product_name = container.find("div", {"class": "KzDlHZ"}).get_text(strip=True) if container.find("div", {"class": "KzDlHZ"}) else "N/A"
            img_url = container.find("img")['src'] if container.find("img") else "N/A"
            current_price = container.find("div", {"class": "Nx9bqj _4b5DiR"}).get_text(strip=True) if container.find("div", {"class": "Nx9bqj _4b5DiR"}) else "N/A"
            original_price = container.find("div", {"class": "yRaY8j ZYYwLA"}).get_text(strip=True) if container.find("div", {"class": "yRaY8j ZYYwLA"}) else "N/A"
            rating = container.find("div", {"class": "XQDdHH"}).get_text(strip=True) if container.find("div", {"class": "XQDdHH"}) else "N/A"
            offers = container.find("div", {"class": "M4DNwV"}).get_text(strip=True) if container.find("div", {"class": "M4DNwV"}) else "No offers available"

            return (product_name, img_url, current_price, original_price, rating, offers, link)
        except Exception as e:
            print(f"Failed to extract product data. Error: {e}")
            return None

    def print_product_data(self, product_name, img_url, current_price, original_price, rating, offers, link):
        print(f"Product Name: {product_name}")
        print(f"Image URL: {img_url}")
        print(f"Current Price: {current_price}")
        print(f"Original Price: {original_price}")
        print(f"Rating: {rating}")
        print(f"Offers: {offers}")
        print(f"Product Link: https://www.flipkart.com{link}\n")


# Example usage
if __name__ == "__main__":
    product = "sonytv"  # Product name to search for
    pages = 2  # Number of pages to scrape
    
    scraper = FlipkartScraper(product, pages)
    scraper.scrape()
