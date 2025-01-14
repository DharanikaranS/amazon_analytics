import mysql.connector
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup
from time import sleep
import random
import re
from datetime import datetime
from abc import ABC, abstractmethod
import threading
import unittest
from unittest.mock import MagicMock, patch
from bs4 import BeautifulSoup

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
            # Replace with your MySQL database details
            self.connection = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="Dharani27#",
                database="ecommerce_analytics",
                connection_timeout=600,
                ssl_disabled=True
            )
            self.cursor = self.connection.cursor()
            DatabaseConnection.__instance = self

            # Create table for Amazon products
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS amazon_products (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    product_type VARCHAR(255),
                                    brand VARCHAR(255),
                                    product_name VARCHAR(255),
                                    retail_price DECIMAL(10, 2),
                                    current_price DECIMAL(10, 2),
                                    rating DECIMAL(2, 1) CHECK (rating >= 0 AND rating <= 5),
                                    offers TEXT
                                )''')

            # Create staging table for Amazon products
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS amazon_products_staging (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    product_type VARCHAR(255),
                                    brand VARCHAR(255),
                                    product_name VARCHAR(255),
                                    retail_price DECIMAL(10, 2),
                                    current_price DECIMAL(10, 2),
                                    rating DECIMAL(2, 1),
                                    offers TEXT
                                )''')

            # Create price history table
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS price_history (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    product_type VARCHAR(50),
                                    product_id INT,
                                    previous_price DECIMAL(10, 2),
                                    new_price DECIMAL(10, 2),
                                    change_date DATETIME,
                                    FOREIGN KEY (product_id) REFERENCES amazon_products(id)
                                )''')

            # Create category average ratings table
            self.cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INT PRIMARY KEY AUTO_INCREMENT,
         UNIQUE (user_id),
        notification_enabled TINYINT(1) DEFAULT 0
                                
    );
''')
            
            # Create stored procedures for product management
            
            self.cursor.execute('''DROP PROCEDURE IF EXISTS update_product_price''')
            self.cursor.execute('''CREATE PROCEDURE update_product_price (
                                        IN prod_id INT,
                                        IN new_price DECIMAL(10, 2)
                                    )
                                    BEGIN
                                        UPDATE amazon_products
                                        SET current_price = new_price
                                        WHERE id = prod_id;
                                    END''')

            self.cursor.execute('''DROP PROCEDURE IF EXISTS insert_price_history''')
            self.cursor.execute('''CREATE PROCEDURE insert_price_history (
                                        IN prod_id INT,
                                        IN prod_type VARCHAR(50),
                                        IN prev_price DECIMAL(10, 2),
                                        IN new_price DECIMAL(10, 2),
                                        IN change_date DATETIME
                                    )
                                    BEGIN
                                        INSERT INTO price_history (product_id, product_type, previous_price, new_price, change_date)
                                        VALUES (prod_id,prod_type, prev_price, new_price, change_date);
                                    END''')



            # Create views for discounted and top-rated products
            self.cursor.execute('''
    CREATE OR REPLACE VIEW discounted_products AS
    SELECT 
        id, 
        product_type,                       
        product_name, 
        brand,
        retail_price, 
        current_price,
        ROUND(((retail_price - current_price) * 100.0 / retail_price), 2) AS discount_percentage
    FROM 
        amazon_products
    WHERE 
        retail_price > current_price
''')




            self.cursor.execute('''
    CREATE OR REPLACE VIEW top_rated_products AS
    SELECT 
        id, 
        product_name, 
        brand,
        current_price, 
        rating
    FROM 
        amazon_products
    WHERE 
        rating >= 4.5
''')

            # Create trigger for validating and moving data from staging to main table
            self.cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS move_valid_products
                AFTER INSERT ON amazon_products_staging
                FOR EACH ROW
                BEGIN
                    IF NEW.retail_price > 0 AND NEW.current_price > 0 AND NEW.rating BETWEEN 0 AND 5
                    AND NEW.retail_price > NEW.current_price THEN
                        INSERT INTO amazon_products (product_type, brand, product_name, retail_price, current_price, rating, offers)
                        VALUES (NEW.product_type, NEW.brand, NEW.product_name, NEW.retail_price, NEW.current_price, NEW.rating, NEW.offers);
                                
    
                    END IF;
                END;
            ''')

            # Create view for frequent brand average rating
            self.cursor.execute('''          
    CREATE OR REPLACE VIEW frequent_brand_avg_rating AS
    SELECT 
        product_type, 
        brand, 
        ROUND(AVG(rating), 2) AS avg_rating
    FROM 
        amazon_products
    GROUP BY 
        product_type, brand
            ''')

            
            self.connection.commit()
            
    def insert_product(self, product_type, brand, product_name, retail_price, current_price, rating, offers):
        query = '''INSERT INTO amazon_products_staging 
                   (product_type, brand, product_name, retail_price, current_price, rating, offers)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)'''
        self.cursor.execute(query, (product_type, brand, product_name, retail_price, current_price, rating, offers))
        self.connection.commit()

    def update_product_price(self, product_id, new_price):
         # Call stored procedure to update product price
        self.cursor.callproc("update_product_price", (product_id, new_price))
        self.connection.commit()

    def insert_price_history(self, product_id, previous_price, new_price):
        # Call stored procedure to insert price history
        change_date = datetime.now()
        self.cursor.callproc("insert_price_history", (product_id,product_type, previous_price, new_price, change_date))
        self.connection.commit()

    def close_connection(self):
        self.cursor.close()
        self.connection.close()

# (Other classes remain the same, such as `Scraper`, `AmazonScraper`, etc.)
class Scraper(ABC):
    def __init__(self, db_connection, product_type, pages):
        self.db = db_connection
        self.product_type = product_type
        self.pages = pages

    @abstractmethod
    def scrape(self):
        pass
# The Amazon Scraper class with dynamic price check
class AmazonScraper(Scraper):

    def scrape(self, is_update=False):
        for page_num in range(1, int(self.pages) + 1):
            print(f"Accessing Amazon page {page_num}")
            my_url = f"https://www.amazon.in/s?k={self.product_type}&page={page_num}"
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
                if product_data:
                    brand, product_title, retail_price, current_price, rating, offers = product_data
                    product_id = self.get_product_id(product_title)

                    if product_id:
                        # If product exists, check for price update
                        self.check_price_update(product_id, current_price)
                    else:
                        # Insert new product if it doesn't exist
                        self.db.insert_product(self.product_type, brand, product_title, retail_price, current_price, rating, offers)
                    self.db.cursor.execute('''DELETE FROM amazon_products_staging WHERE id = %s''', (container.id,))
                    self.db.connection.commit()
            print(f"Amazon page {page_num} finished\n")
            sleep(random.uniform(1.5, 3.5))

    def get_product_id(self, product_name):
        """Retrieve product ID if it already exists in the database."""
        query = '''SELECT id FROM amazon_products WHERE product_name = %s'''
        self.db.cursor.execute(query, (product_name,))

        result = self.db.cursor.fetchone()
        if result:
         product_id = result[0]
         return product_id
        

    def check_price_update(self, product_id, new_price):
     """Check if there's a price change and update accordingly."""
    # Fetch the current price from the database and convert both prices to float for comparison
     self.db.cursor.execute('''SELECT current_price FROM amazon_products WHERE id = %s''', (product_id,))
     current_price = float(self.db.cursor.fetchone()[0])  # Ensure consistent type as float
     if current_price is not None:
        try:
            # Attempt to convert to float
            new_price = float(current_price)
        except (ValueError, TypeError):
            # Handle invalid price value (None or non-numeric)
            print(f"Invalid price for product {product_id}: {current_price}")
            return
    # Normalize new price to float for accurate comparison
        new_price = float(new_price)

    # Proceed only if there’s a true price change
        if current_price != new_price:
        # Log the change in price history and update the main table
         self.db.insert_price_history(product_id, current_price, new_price)
         self.db.update_product_price(product_id, new_price)
         print(f"Price updated for product ID {product_id}: {current_price} -> {new_price}")
     

    def extract_product_data(self, container):
    # Extract product details as before
     product_title = container.h2.get_text(strip=True) if container.h2 else None
     brand = self.extract_brand_from_title(product_title)
    
    # Use None for missing or invalid values
     retail_price = self.clean_price(container.find("span", {"class": "a-price a-text-price"}).get_text(strip=True)) if container.find("span", {"class": "a-price a-text-price"}) else None
     current_price = self.clean_price(container.find("span", {"class": "a-price-whole"}).get_text(strip=True)) if container.find("span", {"class": "a-price-whole"}) else None
     rating = self.extract_numeric_rating(container.find("span", {"class": "a-icon-alt"}).get_text(strip=True)) if container.find("span", {"class": "a-icon-alt"}) else None
     offers = container.find("span", {"class": "a-badge-text"}).get_text(strip=True) if container.find("span", {"class": "a-badge-text"}) else "No offers available"
    
     return (brand, product_title, retail_price, current_price, rating, offers)


    # Additional helper methods
    def extract_brand_from_title(self, title):
        title = re.sub(r'[.!?]', '', title)
        words = title.split()
        brand = words[1] if len(words) > 1 and words[0].lower() == "the" else words[0]
        if len(words) > 1 and (words[0] + " " + words[1]) in ["Johnson & Johnson", "Apple Inc.", "Sony Corporation"]:
            brand = words[0] + " " + words[1]
        return brand

    def clean_price(self, price_str):
        if price_str == "N/A":
            return "N/A"
        price_str = re.sub(r'[^\d.]', '', price_str)
        if len(price_str) % 2 == 0:
            half_len = len(price_str) // 2
            first_half, second_half = price_str[:half_len], price_str[half_len:]
            if first_half == second_half:
                price_str = first_half
        return price_str if price_str else "N/A"

    def extract_numeric_rating(self, rating_str):
     """Extracts the numeric rating from a string like '4.0 out of 5 stars'"""
     match = re.search(r'(\d+\.\d+|\d+)', rating_str)
     return float(match.group()) if match else None

class ScraperFactory:
    def get_scraper(self, platform, db_connection, product_type, pages):
        if platform.lower() == "amazon":
            return AmazonScraper(db_connection, product_type, pages)
        else:
            raise ValueError(f"No scraper available for platform: {platform}")

def run_scraping(scraper, start_page, end_page):
    """Runs scraping for a specific range of pages."""
    for page in range(start_page, end_page + 1):
        print(f"Scraping page {page}")
        scraper.scrape()



class TestAmazonScraper(unittest.TestCase):
    def setUp(self):
        """Set up mock data and objects for testing."""
        self.mock_html = """
        <html>
            <body>
                <div data-component-type="s-search-result">
                    <h2>BrandA Amazing Laptop</h2>
                    <span class="a-price a-text-price">₹1,00,000</span>
                    <span class="a-price-whole">₹95,000</span>
                    <span class="a-icon-alt">4.5 out of 5 stars</span>
                    <span class="a-badge-text">Best Seller</span>
                </div>
                <div data-component-type="s-search-result">
                    <h2>BrandB Another Laptop</h2>
                    <span class="a-price a-text-price">₹80,000</span>
                    <span class="a-price-whole">₹75,000</span>
                    <span class="a-icon-alt">4.0 out of 5 stars</span>
                </div>
            </body>
        </html>
        """
        self.soup = BeautifulSoup(self.mock_html, "html.parser")

        # Mock database connection for tests requiring it
        self.mock_db = MagicMock()

    def test_extract_product_data(self):
        """Test the extraction of product data from HTML containers."""
        from scrapecode import AmazonScraper  # Replace with your file/module name
        
        # Create a mock scraper instance
        scraper = AmazonScraper(self.mock_db, "Laptop", 1)
        
        containers = self.soup.findAll("div", {"data-component-type": "s-search-result"})
        product_data = [scraper.extract_product_data(container) for container in containers]
        
        # Expected data for each container
        expected_data = [
            ("BrandA", "BrandA Amazing Laptop", "100000", "95000", 4.5, "Best Seller"),
            ("BrandB", "BrandB Another Laptop", "80000", "75000", 4.0, "No offers available")
        ]

        self.assertEqual(product_data, expected_data)

    def test_clean_price(self):
        """Test the price cleaning utility function."""
        from scrapecode import AmazonScraper  # Replace with your file/module name
        
        scraper = AmazonScraper(self.mock_db, "Laptop", 1)
        self.assertEqual(scraper.clean_price("₹1,00,000"), "100000")
        self.assertEqual(scraper.clean_price("₹95,000"), "95000")
        self.assertEqual(scraper.clean_price("N/A"), "N/A")

    def test_extract_brand_from_title(self):
        """Test extracting brand name from product title."""
        from scrapecode import AmazonScraper  # Replace with your file/module name
        
        scraper = AmazonScraper(self.mock_db, "Laptop", 1)
        self.assertEqual(scraper.extract_brand_from_title("BrandA Amazing Laptop"), "BrandA")
        self.assertEqual(scraper.extract_brand_from_title("The Amazing Product"), "Amazing")
        self.assertEqual(scraper.extract_brand_from_title("Sony Corporation Amazing TV"), "Sony Corporation")

    def test_extract_numeric_rating(self):
        """Test extracting numeric ratings."""
        from scrapecode import AmazonScraper  # Replace with your file/module name
        
        scraper = AmazonScraper(self.mock_db, "Laptop", 1)
        self.assertEqual(scraper.extract_numeric_rating("4.5 out of 5 stars"), 4.5)
        self.assertEqual(scraper.extract_numeric_rating("No ratings available"), None)


if __name__ == "__main__":
    platform = input("Enter the platform (e.g., Amazon): ")
    product_type = input("Enter the product you want to search for: ")
    pages = int(input("Enter the number of pages to scrape: "))

    db = DatabaseConnection.getInstance()
    factory = ScraperFactory()
    
    try:
        scraper = factory.get_scraper(platform, db, product_type, pages)

        # Define number of threads
        num_threads = 4  # Adjust based on your system's capacity
        pages_per_thread = pages // num_threads
        threads = []

        for i in range(num_threads):
            start_page = i * pages_per_thread + 1
            end_page = (i + 1) * pages_per_thread if i < num_threads - 1 else pages
            thread = threading.Thread(target=run_scraping, args=(scraper, start_page, end_page))
            threads.append(thread)
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

    except ValueError as e:
        print(e)

    db.close_connection()
    print("Multithreaded scraping completed.")

    unittest.main()