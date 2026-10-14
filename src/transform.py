
import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def get_source_id(record):
    value = record.get("_id")

    if isinstance(value, dict):
        return value.get("$oid")

    return str(value) if value is not None else None


def normalize_date(value):
    """Convert MongoDB Extended JSON dates into ISO strings."""
    if value is None:
        return None

    if isinstance(value, dict) and "$date" in value:
        value = value["$date"]

    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(
            value / 1000, tz=timezone.utc
        ).isoformat()

    if isinstance(value, str):
        return value

    return None


def read_records(name):
    path = RAW_DIR / f"{name}.json"

    with path.open("r", encoding="utf-8") as file:
        records = json.load(file)

    return records if isinstance(records, list) else [records]


def write_records(name, records):
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    path = PROCESSED_DIR / f"{name}.json"

    with path.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2, ensure_ascii=False)

    print(f"{name}: wrote {len(records)} records")


def transform_users(records):
    result = []

    for user in records:
        # Only select fields needed for reporting.
        # Do not copy passwords, phone numbers, carts, or price maps.
        result.append({
            "source_user_id": get_source_id(user),
            "first_name": user.get("fname"),
            "last_name": user.get("lname"),
            "email": user.get("email"),
            "city": user.get("city"),
            "state": user.get("state"),
            "group_id": user.get("group_id"),
            "user_type": user.get("user_type"),
            "created_at": normalize_date(user.get("created_at")),
        })

    return result


def transform_orders(records):
    orders = []
    order_items = []

    for order in records:
        order_id = get_source_id(order)

        orders.append({
            "source_order_id": order_id,
            "source_user_id": order.get("user_id"),
            "group_id": order.get("group_id"),
            "status": order.get("status"),
            "total_amount": order.get("total_amt"),
            "savings_total": order.get("savings_total"),
            "created_at": normalize_date(order.get("created_at")),
        })

        products = order.get("products", [])

        if not isinstance(products, list):
            continue

        for index, product in enumerate(products):
            if not isinstance(product, dict):
                continue

            order_items.append({
                "source_order_id": order_id,
                "source_item_index": index,
                "product_id": product.get("product_id"),
                "supplier": product.get("supplier"),
                "supplier_product_id": product.get(
                    "supplier_product_id"
                ),
                "product_name": product.get("name"),
                "quantity": product.get("qty"),
                "unit_price": product.get("unit_price"),
                "item_amount": product.get("price"),
            })

    return orders, order_items


def transform_bills(records):
    bills = []
    bill_line_items = []

    for bill in records:
        bill_id = get_source_id(bill)

        bills.append({
            "source_bill_id": bill_id,
            "group_id": bill.get("group_id"),
            "supplier": bill.get("supplier"),
            "invoice_number": bill.get("inv_num"),
            "invoice_date": normalize_date(bill.get("inv_date")),
            "due_date": normalize_date(bill.get("due_date")),
            "status": bill.get("status"),
            "subtotal": bill.get("sub_total"),
            "taxes": bill.get("taxes"),
            "shipping": bill.get("shipping"),
            "total_amount": bill.get("total"),
            "paid_amount": bill.get("paid_amount"),
        })

        items = bill.get("line_items", [])

        if not isinstance(items, list):
            continue

        for index, item in enumerate(items):
            if not isinstance(item, dict):
                continue

            bill_line_items.append({
                "source_bill_id": bill_id,
                "source_item_index": index,
                "supplier_product_id": item.get(
                    "supplier_product_id"
                ),
                "item_name": item.get("name"),
                "quantity": item.get("qty"),
                "unit_price": item.get("unit_price"),
                "item_amount": item.get("price"),
            })

    return bills, bill_line_items


def main():
    users_raw = read_records("users")
    orders_raw = read_records("orders")
    bills_raw = read_records("bills")

    users = transform_users(users_raw)
    orders, order_items = transform_orders(orders_raw)
    bills, bill_line_items = transform_bills(bills_raw)

    write_records("users", users)
    write_records("orders", orders)
    write_records("order_items", order_items)
    write_records("bills", bills)
    write_records("bill_line_items", bill_line_items)

    print("Transformation completed successfully.")


if __name__ == "__main__":
    main()
