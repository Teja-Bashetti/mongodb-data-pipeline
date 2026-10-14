
USE mongodb_data_pipeline;

-- Dimension: users
CREATE TABLE IF NOT EXISTS dim_user (
    user_key INT AUTO_INCREMENT PRIMARY KEY,
    source_user_id VARCHAR(100) NOT NULL UNIQUE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    user_type JSON
);

-- Dimension: products
CREATE TABLE IF NOT EXISTS dim_product (
    product_key INT AUTO_INCREMENT PRIMARY KEY,
    source_product_id VARCHAR(100),
    product_name VARCHAR(500),
    supplier VARCHAR(100),
    supplier_product_id VARCHAR(150)
);

-- Dimension: dates
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL,
    year_num INT,
    month_num INT,
    day_num INT
);

-- Fact: order header measures
CREATE TABLE IF NOT EXISTS fact_order (
    order_key INT AUTO_INCREMENT PRIMARY KEY,
    source_order_id VARCHAR(100) NOT NULL UNIQUE,
    user_key INT,
    order_date_key INT,
    order_status VARCHAR(50),
    total_amount DECIMAL(14,2),
    savings_total DECIMAL(14,2),
    FOREIGN KEY (user_key) REFERENCES dim_user(user_key),
    FOREIGN KEY (order_date_key) REFERENCES dim_date(date_key)
);

-- Fact: order line-item measures
CREATE TABLE IF NOT EXISTS fact_order_item (
    order_item_key BIGINT AUTO_INCREMENT PRIMARY KEY,
    source_order_id VARCHAR(100) NOT NULL,
    source_item_index INT NOT NULL,
    product_key INT,
    quantity DECIMAL(12,3),
    unit_price DECIMAL(14,4),
    item_amount DECIMAL(14,2),
    UNIQUE (source_order_id, source_item_index),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key)
);
