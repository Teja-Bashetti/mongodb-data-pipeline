
USE mongodb_data_pipeline;

-- 1. Load normalized locations
INSERT INTO dim_location (city, state)
SELECT DISTINCT u.city, u.state
FROM stg_users u
WHERE NOT EXISTS (
    SELECT 1
    FROM dim_location l
    WHERE l.city <=> u.city
      AND l.state <=> u.state
);

-- 2. Load suppliers from order items and bills
INSERT INTO dim_product_supplier (supplier_name)
SELECT DISTINCT TRIM(x.supplier_name)
FROM (
    SELECT supplier AS supplier_name
    FROM order_items
    UNION
    SELECT supplier AS supplier_name
    FROM stg_bills
) x
WHERE x.supplier_name IS NOT NULL
  AND TRIM(x.supplier_name) <> ''
ON DUPLICATE KEY UPDATE
    supplier_name = VALUES(supplier_name);

-- 3. Load normalized users
INSERT INTO dim_user_snowflake (
    source_user_id, first_name, last_name,
    email, location_key, user_type
)
SELECT
    u.source_user_id,
    u.first_name,
    u.last_name,
    u.email,
    l.location_key,
    u.user_type
FROM stg_users u
LEFT JOIN dim_location l
    ON l.city <=> u.city
   AND l.state <=> u.state
ON DUPLICATE KEY UPDATE
    first_name = VALUES(first_name),
    last_name = VALUES(last_name),
    email = VALUES(email),
    location_key = VALUES(location_key),
    user_type = VALUES(user_type);

-- 4. Load normalized products
INSERT INTO dim_product_snowflake (
    source_product_id, product_name,
    supplier_product_id, supplier_key
)
SELECT DISTINCT
    oi.product_id,
    oi.product_name,
    oi.supplier_product_id,
    s.supplier_key
FROM order_items oi
LEFT JOIN dim_product_supplier s
    ON s.supplier_name = TRIM(oi.supplier)
WHERE NOT EXISTS (
    SELECT 1
    FROM dim_product_snowflake p
    WHERE p.source_product_id <=> oi.product_id
      AND p.product_name <=> oi.product_name
      AND p.supplier_product_id <=> oi.supplier_product_id
      AND p.supplier_key <=> s.supplier_key
);

-- 5. Load order facts
INSERT INTO fact_order_snowflake (
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
LEFT JOIN dim_user_snowflake u
    ON u.source_user_id = o.source_user_id
ON DUPLICATE KEY UPDATE
    user_key = VALUES(user_key),
    order_date_key = VALUES(order_date_key),
    order_status = VALUES(order_status),
    total_amount = VALUES(total_amount),
    savings_total = VALUES(savings_total);

-- 6. Load order-item facts
INSERT INTO fact_order_item_snowflake (
    source_order_id, source_item_index,
    product_key, quantity, unit_price, item_amount
)
SELECT
    oi.source_order_id,
    oi.source_item_index,
    p.product_key,
    oi.quantity,
    oi.unit_price,
    oi.item_amount
FROM order_items oi
LEFT JOIN dim_product_supplier s
    ON s.supplier_name = TRIM(oi.supplier)
LEFT JOIN dim_product_snowflake p
    ON p.source_product_id <=> oi.product_id
   AND p.product_name <=> oi.product_name
   AND p.supplier_product_id <=> oi.supplier_product_id
   AND p.supplier_key <=> s.supplier_key
ON DUPLICATE KEY UPDATE
    product_key = VALUES(product_key),
    quantity = VALUES(quantity),
    unit_price = VALUES(unit_price),
    item_amount = VALUES(item_amount);
