import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
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
    def __init__(self, db_connection, product, pages, driver):
        self.db = db_connection
        self.product = product
        self.pages = pages
        self.driver = driver

    def scrape(self):
        raise NotImplementedError("Scrape method must be implemented by subclasses")

# Step 3: Implement Amazon and Flipkart Scraper Classes using Selenium
class AmazonScraper(ProductScraper):
    def scrape(self):
        for page_num in range(1, int(self.pages) + 1):
            print(f"Accessing Amazon page {page_num}")
            my_url = f"https://www.amazon.in/s?k={self.product}&page={page_num}"
            self.driver.get(my_url)

            sleep(random.uniform(1.5, 3.5))

            containers = self.driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")

            for container in containers:
                product_data = self.extract_product_data(container)
                self.db.insert_product("amazon_products", *product_data)

            print(f"Amazon page {page_num} finished\n")

    def extract_product_data(self, container):
        try:
            brand = container.find_element(By.CSS_SELECTOR, "span.a-size-base-plus").text
        except:
            brand = "N/A"
        
        try:
            product_name = container.find_element(By.CSS_SELECTOR, "h2 span").text
        except:
            product_name = "N/A"
        
        try:
            retail_price = container.find_element(By.CSS_SELECTOR, "span.a-price.a-text-price span.a-offscreen").text
        except:
            retail_price = "N/A"
        
        try:
            current_price = container.find_element(By.CSS_SELECTOR, "span.a-price-whole").text
        except:
            current_price = "N/A"
        
        try:
            rating = container.find_element(By.CSS_SELECTOR, "span.a-icon-alt").text
        except:
            rating = "N/A"
        
        try:
            offers = container.find_element(By.CSS_SELECTOR, "span.a-badge-text").text
        except:
            offers = "No offers available"
        
        return (brand, product_name, retail_price, current_price, rating, offers)

'''class FlipkartScraper(ProductScraper):
    def scrape(self):
        for page_num in range(1, int(self.pages) + 1):
            print(f"Accessing Flipkart page {page_num}")
            my_url = f"https://www.flipkart.com/search?q={self.product}&page={page_num}"
            self.driver.get(my_url)

            sleep(random.uniform(1.5, 3.5))

            containers = self.driver.find_elements(By.CSS_SELECTOR, "div._1AtVbE")

            for container in containers:
                product_data = self.extract_product_data(container)
                self.db.insert_product("flipkart_products", *product_data)

            print(f"Flipkart page {page_num} finished\n")

    def extract_product_data(self, container):
        try:
            brand = container.find_element(By.CSS_SELECTOR, "div._2WkVRV").text
        except:
            brand = "N/A"
        
        try:
            product_name = container.find_element(By.CSS_SELECTOR, "a.IRpwTa").text
        except:
            product_name = "N/A"
        
        try:
            retail_price = container.find_element(By.CSS_SELECTOR, "div._3I9_wc").text
        except:
            retail_price = "N/A"
        
        try:
            current_price = container.find_element(By.CSS_SELECTOR, "div._30jeq3").text
        except:
            current_price = "N/A"
        
        try:
            rating = container.find_element(By.CSS_SELECTOR, "div._3LWZlK").text
        except:
            rating = "N/A"
        
        offers = "Offers available" if container.find_element(By.CSS_SELECTOR, "div._2Z4mvk") else "No offers available"
        
        return (brand, product_name, retail_price, current_price, rating, offers)'''
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up the Chrome driver with SSL options and more waiting time
chrome_options = Options()
chrome_options.add_argument("--disable-ssl-errors")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--headless")  # Optional, for headless mode
service = Service(executable_path="C:\\chromedriver-win64\\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

class FlipkartScraper(ProductScraper):
    def scrape(self):
        for page_num in range(1, int(self.pages) + 1):
            print(f"Accessing Flipkart page {page_num}")
            my_url = f"https://www.flipkart.com/search?q={self.product}&page={page_num}"
            self.driver.get(my_url)

            # Wait for the product containers to be loaded
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div._1AtVbE"))
                )
            except Exception as e:
                print(f"Timeout: Flipkart page {page_num} elements not loaded in time. Error: {e}")
                continue

            # Optionally, scroll down to load more content
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(random.uniform(2, 4))  # Adding some delay

            containers = self.driver.find_elements(By.CSS_SELECTOR, "div._1AtVbE")

            if containers:
                for container in containers:
                    product_data = self.extract_product_data(container)
                    self.db.insert_product("flipkart_products", *product_data)

                print(f"Flipkart page {page_num} finished\n")
            else:
                print(f"No product containers found on Flipkart page {page_num}. Skipping...\n")

            sleep(random.uniform(1.5, 3.5))

    def extract_product_data(self, container):
        try:
            brand = container.find_element(By.CSS_SELECTOR, "div._2WkVRV").text
        except:
            brand = "N/A"
        
        try:
            product_name = container.find_element(By.CSS_SELECTOR, "a.IRpwTa").text
        except:
            product_name = "N/A"
        
        try:
            retail_price = container.find_element(By.CSS_SELECTOR, "div._3I9_wc").text
        except:
            retail_price = "N/A"
        
        try:
            current_price = container.find_element(By.CSS_SELECTOR, "div._30jeq3").text
        except:
            current_price = "N/A"
        
        try:
            rating = container.find_element(By.CSS_SELECTOR, "div._3LWZlK").text
        except:
            rating = "N/A"
        
        offers = "Offers available" if container.find_element(By.CSS_SELECTOR, "div._2Z4mvk") else "No offers available"
        
        return (brand, product_name, retail_price, current_price, rating, offers)

# Step 4: Create a Factory to get the appropriate Scraper instance
class ScraperFactory:
    @staticmethod
    def get_scraper(platform, db_connection, product, pages, driver):
        if platform.lower() == "amazon":
            return AmazonScraper(db_connection, product, pages, driver)
        elif platform.lower() == "flipkart":
            return FlipkartScraper(db_connection, product, pages, driver)
        else:
            raise ValueError("Unknown platform specified")

# Step 5: Set up Selenium WebDriver and run the Scraping Process
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Runs Chrome in headless mode (no GUI)
    chrome_options.add_argument("--disable-gpu")  # Disables GPU hardware acceleration

    # Path to the chromedriver executable
    service = Service("C:\\chromedriver-win64\\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

if __name__ == "__main__":
    product = input("Enter the product you want to search for: ")
    pages = input("Enter the number of pages to scrape: ")

    db = DatabaseConnection.getInstance()

    # Set up Selenium WebDriver
    driver = setup_driver()

    # Amazon Scraping
    amazon_scraper = ScraperFactory.get_scraper("amazon", db, product, pages, driver)
    amazon_scraper.scrape()

    # Flipkart Scraping
    flipkart_scraper = ScraperFactory.get_scraper("flipkart", db, product, pages, driver)
    flipkart_scraper.scrape()

    # Close the browser and database connection
    driver.quit()
    db.close_connection()

    print("Scraping completed for both Amazon and Flipkart.")
