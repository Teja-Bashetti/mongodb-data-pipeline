
USE mongodb_data_pipeline;

-- 1. Load users dimension
INSERT INTO dim_user (
    source_user_id, first_name, last_name,
    email, city, state, user_type
)
SELECT
    source_user_id, first_name, last_name,
    email, city, state, user_type
FROM stg_users
ON DUPLICATE KEY UPDATE
    first_name = VALUES(first_name),
    last_name = VALUES(last_name),
    email = VALUES(email),
    city = VALUES(city),
    state = VALUES(state),
    user_type = VALUES(user_type);

-- 2. Load product dimension from order items
INSERT INTO dim_product (
    source_product_id, product_name,
    supplier, supplier_product_id
)
SELECT DISTINCT
    oi.product_id,
    oi.product_name,
    oi.supplier,
    oi.supplier_product_id
FROM order_items oi
WHERE NOT EXISTS (
    SELECT 1
    FROM dim_product dp
    WHERE dp.source_product_id <=> oi.product_id
      AND dp.product_name <=> oi.product_name
      AND dp.supplier <=> oi.supplier
      AND dp.supplier_product_id <=> oi.supplier_product_id
);

-- 3. Load date dimension from order creation dates
INSERT INTO dim_date (
    date_key, full_date, year_num, month_num, day_num
)
SELECT DISTINCT
    CAST(DATE_FORMAT(created_at, '%Y%m%d') AS UNSIGNED),
    DATE(created_at),
    YEAR(created_at),
    MONTH(created_at),
    DAYOFMONTH(created_at)
FROM stg_orders
WHERE created_at IS NOT NULL
ON DUPLICATE KEY UPDATE
    full_date = VALUES(full_date);

-- 4. Load order fact
INSERT INTO fact_order (
    source_order_id, user_key, order_date_key,
    order_status, total_amount, savings_total
)
SELECT
    o.source_order_id,
    u.user_key,
    CASE
        WHEN o.created_at IS NOT NULL
        THEN CAST(DATE_FORMAT(o.created_at, '%Y%m%d') AS UNSIGNED)
        ELSE NULL
    END,
    o.status,
    o.total_amount,
    o.savings_total
FROM stg_orders o
LEFT JOIN dim_user u
    ON u.source_user_id = o.source_user_id
ON DUPLICATE KEY UPDATE
    user_key = VALUES(user_key),
    order_date_key = VALUES(order_date_key),
    order_status = VALUES(order_status),
    total_amount = VALUES(total_amount),
    savings_total = VALUES(savings_total);

-- 5. Load order-item fact
INSERT INTO fact_order_item (
    source_order_id, source_item_index,
    product_key, quantity, unit_price, item_amount
)
SELECT
    oi.source_order_id,
    oi.source_item_index,
    dp.product_key,
    oi.quantity,
    oi.unit_price,
    oi.item_amount
FROM order_items oi
LEFT JOIN dim_product dp
    ON dp.source_product_id <=> oi.product_id
   AND dp.product_name <=> oi.product_name
   AND dp.supplier <=> oi.supplier
   AND dp.supplier_product_id <=> oi.supplier_product_id
ON DUPLICATE KEY UPDATE
    product_key = VALUES(product_key),
    quantity = VALUES(quantity),
    unit_price = VALUES(unit_price),
    item_amount = VALUES(item_amount);
