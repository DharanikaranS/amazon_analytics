'''import sqlite3

class DatabaseConnection:
    __instance = None
    
    @staticmethod
    def getInstance():
        """ Static access method. """
        if DatabaseConnection.__instance is None:
            DatabaseConnection()
        return DatabaseConnection.__instance

    def __init__(self):
        """ Private constructor for singleton database connection. """
        if DatabaseConnection.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            # Initialize database connection
            self.connection = sqlite3.connect("amazon_products.db")
            self.cursor = self.connection.cursor()
            DatabaseConnection.__instance = self
            
            # Create table if it doesn't exist
            self.cursor.execute('CREATE TABLE IF NOT EXISTS products (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    brand TEXT,
                                    product_name TEXT,
                                    retail_price TEXT,
                                    current_price TEXT,
                                    rating TEXT,
                                    offers TEXT
                                )')
            self.connection.commit()
    
    def insert_product(self, brand, product_name, retail_price, current_price, rating, offers):
        """ Method to insert a new product into the database. """
        self.cursor.execute("INSERT INTO products (brand, product_name, retail_price, current_price, rating, offers) VALUES (?, ?, ?, ?, ?, ?)", 
                            (brand, product_name, retail_price, current_price, rating, offers))
        self.connection.commit()
        
    def close_connection(self):
        """ Close the database connection. """
        self.connection.close()

    

    

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup
from time import sleep
import random
import os

# Centered Header for Terminal Output
width = os.get_terminal_size().columns
print("\n\n\n" + "Amazon Web Scraping".center(width))

# User inputs
product=input("Enter the product you want:")
inp =  f'https://www.amazon.in/s?k={product}'
pg = input("Enter the number of pages to scrape: ")

# Initialize singleton database instance
db = DatabaseConnection.getInstance()

# Loop through pages
for page_num in range(1, int(pg) + 1):
    print(f"Accessing page {page_num}")
    my_url = f"{inp}{page_num}"
    
    # Setting up request with User-Agent
    req = Request(my_url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        page_html = urlopen(req).read()
    except Exception as e:
        print(f"Failed to retrieve page {page_num}. Error: {e}")
        continue

    page_soup = soup(page_html, "html.parser")

    # Adjusted container class for Amazon's current HTML structure
    containers = page_soup.findAll("div", {"data-component-type": "s-search-result"})

    # Extract data from each product listing
    for container in containers:
        try:
            product_name = container.h2.get_text().strip()
        except AttributeError:
            product_name = "N/A"
        
        try:
            price = container.find("span", {"class": "a-price-whole"}).get_text(strip=True)
        except AttributeError:
            price = "N/A"

        try:
            rating = container.find("span", {"class": "a-icon-alt"}).get_text(strip=True)
        except AttributeError:
            rating = "N/A"

        try:
            brand = container.find("span", {"class": "a-size-base-plus"}).get_text(strip=True)
        except AttributeError:
            brand = "N/A"

        try:
            retail_price = container.find("span", {"class": "a-price a-text-price"}).get_text(strip=True)
        except AttributeError:
            retail_price = "N/A"

        try:
            offers = container.find("span", {"class": "a-badge-text"}).get_text(strip=True)
        except AttributeError:
            offers = "No offers available"

        # Insert data into the database
        db.insert_product(product, product_name, retail_price, price, rating, offers)

    print(f"Page {page_num} finished\n")
    # Sleep to avoid being detected as a bot
    sleep(random.uniform(1.5, 3.5))

print("Scraping completed.")

# Close the database connection after scraping
db.close_connection()
'''
import sqlite3
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup
from time import sleep
import random

# Step 1: Database Singleton with separate tables for Amazon and Flipkart
class DatabaseConnection:
    __instance = None

    @staticmethod
    def getInstance():
        if DatabaseConnection.__instance is None:
            DatabaseConnection()
        return DatabaseConnection.__instance

    def __init__(self):
        if DatabaseConnection.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.connection = sqlite3.connect("ecommerce_products.db")
            self.cursor = self.connection.cursor()
            DatabaseConnection.__instance = self
            
            # Create tables for Amazon and Flipkart if they do not exist
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS amazon_products (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    brand TEXT,
                                    product_name TEXT,
                                    retail_price TEXT,
                                    current_price TEXT,
                                    rating TEXT,
                                    offers TEXT
                                )''')
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS flipkart_products (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    brand TEXT,
                                    product_name TEXT,
                                    retail_price TEXT,
                                    current_price TEXT,
                                    rating TEXT,
                                    offers TEXT
                                )''')
            self.connection.commit()

    def insert_product(self, table, brand, product_name, retail_price, current_price, rating, offers):
        query = f"INSERT INTO {table} (brand, product_name, retail_price, current_price, rating, offers) VALUES (?, ?, ?, ?, ?, ?)"
        self.cursor.execute(query, (brand, product_name, retail_price, current_price, rating, offers))
        self.connection.commit()
        
    def close_connection(self):
        self.connection.close()

# Step 2: Define the Scraper Interface
class ProductScraper:
    def __init__(self, db_connection, product, pages):
        self.db = db_connection
        self.product = product
        self.pages = pages

    def scrape(self):
        raise NotImplementedError("Scrape method must be implemented by subclasses")

# Step 3: Implement Amazon and Flipkart Scraper Classes
class AmazonScraper(ProductScraper):
    def scrape(self):
        for page_num in range(1, int(self.pages) + 1):
            print(f"Accessing Amazon page {page_num}")
            my_url = f"https://www.amazon.in/s?k={self.product}&page={page_num}"
            req = Request(my_url, headers={'User-Agent': 'Mozilla/5.0'})
            
            try:
                page_html = urlopen(req).read()
            except Exception as e:
                print(f"Failed to retrieve Amazon page {page_num}. Error: {e}")
                continue

            page_soup = soup(page_html, "html.parser")
            containers = page_soup.findAll("div", {"data-component-type": "s-search-result"})

            for container in containers:
                product_data = self.extract_product_data(container)
                self.db.insert_product("amazon_products", *product_data)

            print(f"Amazon page {page_num} finished\n")
            sleep(random.uniform(1.5, 3.5))
    
    def extract_product_data(self, container):
        brand = container.find("span", {"class": "a-size-base-plus"}).get_text(strip=True) if container.find("span", {"class": "a-size-base-plus"}) else "N/A"
        product_name = container.h2.get_text(strip=True) if container.h2 else "N/A"
        retail_price = container.find("span", {"class": "a-price a-text-price"}).get_text(strip=True) if container.find("span", {"class": "a-price a-text-price"}) else "N/A"
        current_price = container.find("span", {"class": "a-price-whole"}).get_text(strip=True) if container.find("span", {"class": "a-price-whole"}) else "N/A"
        rating = container.find("span", {"class": "a-icon-alt"}).get_text(strip=True) if container.find("span", {"class": "a-icon-alt"}) else "N/A"
        offers = container.find("span", {"class": "a-badge-text"}).get_text(strip=True) if container.find("span", {"class": "a-badge-text"}) else "No offers available"
        
        return (brand, product_name, retail_price, current_price, rating, offers)

class FlipkartScraper(ProductScraper):
    def scrape(self):
        for page_num in range(1, int(self.pages) + 1):
            print(f"Accessing Flipkart page {page_num}")
            my_url = f"https://www.flipkart.com/search?q={self.product}&page={page_num}"
            req = Request(my_url, headers={'User-Agent': 'Mozilla/5.0'})
            
            try:
                page_html = urlopen(req).read()
            except Exception as e:
                print(f"Failed to retrieve Flipkart page {page_num}. Error: {e}")
                continue

            page_soup = soup(page_html, "html.parser")
            containers = page_soup.findAll("div", {"class": "_1AtVbE"})

            for container in containers:
                product_data = self.extract_product_data(container)
                self.db.insert_product("flipkart_products", *product_data)

            print(f"Flipkart page {page_num} finished\n")
            sleep(random.uniform(1.5, 3.5))
    
    def extract_product_data(self, container):
        brand = container.find("div", {"class": "_2WkVRV"}).get_text(strip=True) if container.find("div", {"class": "_2WkVRV"}) else "N/A"
        product_name = container.find("a", {"class": "IRpwTa"}).get_text(strip=True) if container.find("a", {"class": "IRpwTa"}) else "N/A"
        retail_price = container.find("div", {"class": "_3I9_wc"}).get_text(strip=True) if container.find("div", {"class": "_3I9_wc"}) else "N/A"
        current_price = container.find("div", {"class": "_30jeq3"}).get_text(strip=True) if container.find("div", {"class": "_30jeq3"}) else "N/A"
        rating = container.find("div", {"class": "_3LWZlK"}).get_text(strip=True) if container.find("div", {"class": "_3LWZlK"}) else "N/A"
        offers = "Offers available" if container.find("div", {"class": "_2Z4mvk"}) else "No offers available"
        
        return (brand, product_name, retail_price, current_price, rating, offers)

# Step 4: Create a Factory to get the appropriate Scraper instance
class ScraperFactory:
    @staticmethod
    def get_scraper(platform, db_connection, product, pages):
        if platform.lower() == "amazon":
            return AmazonScraper(db_connection, product, pages)
        elif platform.lower() == "flipkart":
            return FlipkartScraper(db_connection, product, pages)
        else:
            raise ValueError("Unknown platform specified")

# Step 5: Run the Scraping Process
if __name__ == "__main__":
    product = input("Enter the product you want to search for: ")
    pages = input("Enter the number of pages to scrape: ")

    db = DatabaseConnection.getInstance()
    
    # Amazon Scraping
    amazon_scraper = ScraperFactory.get_scraper("amazon", db, product, pages)
    amazon_scraper.scrape()

    # Flipkart Scraping
    flipkart_scraper = ScraperFactory.get_scraper("flipkart", db, product, pages)
    flipkart_scraper.scrape()

    db.close_connection()
    print("Scraping completed for both Amazon and Flipkart.")
