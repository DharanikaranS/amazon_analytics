USE ecommerce_analytics;
select * from amazon_products;
DELIMITER $$

CREATE PROCEDURE InsertProduct(
    IN p_product_type VARCHAR(255),
    IN p_brand VARCHAR(255),
    IN p_product_name VARCHAR(255),
    IN p_retail_price DECIMAL(10, 2),
    IN p_current_price DECIMAL(10, 2),
    IN p_rating DECIMAL(2, 1),
    IN p_offers TEXT
)
BEGIN
    INSERT INTO amazon_products_staging 
    (product_type, brand, product_name, retail_price, current_price, rating, offers)
    VALUES (p_product_type, p_brand, p_product_name, p_retail_price, p_current_price, p_rating, p_offers);
END $$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE UpdateProductPrice(
    IN p_product_id INT,
    IN p_new_price DECIMAL(10, 2)
)
BEGIN
    UPDATE amazon_products SET current_price = p_new_price WHERE id = p_product_id;
END $$

DELIMITER ;
DELIMITER $$

CREATE PROCEDURE InsertPriceHistory(
    IN p_product_id INT,
    IN p_previous_price DECIMAL(10, 2),
    IN p_new_price DECIMAL(10, 2)
)
BEGIN
    INSERT INTO price_history (product_id, previous_price, new_price, change_date)
    VALUES (p_product_id, p_previous_price, p_new_price, NOW());
END $$

DELIMITER ;
DELIMITER $$




