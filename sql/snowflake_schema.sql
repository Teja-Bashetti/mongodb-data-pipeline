
USE mongodb_data_pipeline;

-- 1. Normalize location details
CREATE TABLE IF NOT EXISTS dim_location (
    location_key INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100),
    state VARCHAR(100),
    UNIQUE KEY uq_location (city, state)
);

-- 2. Normalized user dimension
CREATE TABLE IF NOT EXISTS dim_user_snowflake (
    user_key INT AUTO_INCREMENT PRIMARY KEY,
    source_user_id VARCHAR(100) NOT NULL UNIQUE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    location_key INT,
    user_type JSON,
    FOREIGN KEY (location_key)
        REFERENCES dim_location(location_key)
);

-- 3. Normalized product supplier details
CREATE TABLE IF NOT EXISTS dim_product_supplier (
    supplier_key INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_product_snowflake (
    product_key INT AUTO_INCREMENT PRIMARY KEY,
    source_product_id VARCHAR(100),
    product_name VARCHAR(500),
    supplier_product_id VARCHAR(150),
    supplier_key INT,
    FOREIGN KEY (supplier_key)
        REFERENCES dim_product_supplier(supplier_key)
);

-- 4. Fact table for orders
CREATE TABLE IF NOT EXISTS fact_order_snowflake (
    order_key INT AUTO_INCREMENT PRIMARY KEY,
    source_order_id VARCHAR(100) NOT NULL UNIQUE,
    user_key INT,
    order_date_key INT,
    order_status VARCHAR(50),
    total_amount DECIMAL(14,2),
    savings_total DECIMAL(14,2),
    FOREIGN KEY (user_key)
        REFERENCES dim_user_snowflake(user_key),
    FOREIGN KEY (order_date_key)
        REFERENCES dim_date(date_key)
);

-- 5. Order item fact
CREATE TABLE IF NOT EXISTS fact_order_item_snowflake (
    order_item_key BIGINT AUTO_INCREMENT PRIMARY KEY,
    source_order_id VARCHAR(100) NOT NULL,
    source_item_index INT NOT NULL,
    product_key INT,
    quantity DECIMAL(12,3),
    unit_price DECIMAL(14,4),
    item_amount DECIMAL(14,2),
    UNIQUE KEY uq_order_item (source_order_id, source_item_index),
    FOREIGN KEY (product_key)
        REFERENCES dim_product_snowflake(product_key)
);
