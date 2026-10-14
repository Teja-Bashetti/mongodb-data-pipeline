
import json
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv
import mysql.connector

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def read_records(name):
    path = PROCESSED_DIR / f"{name}.json"

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def parse_datetime(value):
    if not value:
        return None

    # Convert ISO timestamps to MySQL DATETIME.
    value = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(value)

    # MySQL DATETIME stores no timezone.
    # Convert aware timestamps to UTC before removing timezone.
    if dt.tzinfo is not None:
        dt = dt.astimezone(
            __import__("datetime").timezone.utc
        ).replace(tzinfo=None)

    return dt


def parse_decimal(value):
    if value is None:
        return None

    return Decimal(str(value))


def main():
    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv(
            "MYSQL_DATABASE", "mongodb_data_pipeline"
        ),
    )

    try:
        cursor = connection.cursor()

        # Load parent tables before child tables because of foreign keys.
        users = read_records("users")
        orders = read_records("orders")
        order_items = read_records("order_items")
        bills = read_records("bills")
        bill_items = read_records("bill_line_items")

        cursor.executemany(
            """
            INSERT INTO stg_users
            (source_user_id, first_name, last_name, email,
             city, state, group_id, user_type, created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
                first_name=VALUES(first_name),
                last_name=VALUES(last_name),
                email=VALUES(email),
                city=VALUES(city),
                state=VALUES(state),
                group_id=VALUES(group_id),
                user_type=VALUES(user_type),
                created_at=VALUES(created_at)
            """,
            [
                (
                    r["source_user_id"],
                    r["first_name"],
                    r["last_name"],
                    r["email"],
                    r["city"],
                    r["state"],
                    r["group_id"],
                    json.dumps(r["user_type"]),
                    parse_datetime(r["created_at"]),
                )
                for r in users
            ],
        )

        cursor.executemany(
            """
            INSERT INTO stg_orders
            (source_order_id, source_user_id, group_id,
             status, total_amount, savings_total, created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
                source_user_id=VALUES(source_user_id),
                group_id=VALUES(group_id),
                status=VALUES(status),
                total_amount=VALUES(total_amount),
                savings_total=VALUES(savings_total),
                created_at=VALUES(created_at)
            """,
            [
                (
                    r["source_order_id"],
                    r["source_user_id"],
                    r["group_id"],
                    r["status"],
                    parse_decimal(r["total_amount"]),
                    parse_decimal(r["savings_total"]),
                    parse_datetime(r["created_at"]),
                )
                for r in orders
            ],
        )

        cursor.executemany(
            """
            INSERT INTO order_items
            (source_order_id, source_item_index, product_id,
             supplier, supplier_product_id, product_name,
             quantity, unit_price, item_amount)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
                product_id=VALUES(product_id),
                supplier=VALUES(supplier),
                supplier_product_id=VALUES(supplier_product_id),
                product_name=VALUES(product_name),
                quantity=VALUES(quantity),
                unit_price=VALUES(unit_price),
                item_amount=VALUES(item_amount)
            """,
            [
                (
                    r["source_order_id"],
                    r["source_item_index"],
                    r["product_id"],
                    r["supplier"],
                    r["supplier_product_id"],
                    r["product_name"],
                    parse_decimal(r["quantity"]),
                    parse_decimal(r["unit_price"]),
                    parse_decimal(r["item_amount"]),
                )
                for r in order_items
            ],
        )

        cursor.executemany(
            """
            INSERT INTO stg_bills
            (source_bill_id, group_id, supplier, invoice_number,
             invoice_date, due_date, status, subtotal, taxes,
             shipping, total_amount, paid_amount)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
                group_id=VALUES(group_id),
                supplier=VALUES(supplier),
                invoice_number=VALUES(invoice_number),
                invoice_date=VALUES(invoice_date),
                due_date=VALUES(due_date),
                status=VALUES(status),
                subtotal=VALUES(subtotal),
                taxes=VALUES(taxes),
                shipping=VALUES(shipping),
                total_amount=VALUES(total_amount),
                paid_amount=VALUES(paid_amount)
            """,
            [
                (
                    r["source_bill_id"],
                    r["group_id"],
                    r["supplier"],
                    r["invoice_number"],
                    parse_datetime(r["invoice_date"]),
                    parse_datetime(r["due_date"]),
                    r["status"],
                    parse_decimal(r["subtotal"]),
                    parse_decimal(r["taxes"]),
                    parse_decimal(r["shipping"]),
                    parse_decimal(r["total_amount"]),
                    parse_decimal(r["paid_amount"]),
                )
                for r in bills
            ],
        )

        cursor.executemany(
            """
            INSERT INTO bill_line_items
            (source_bill_id, source_item_index, supplier_product_id,
             item_name, quantity, unit_price, item_amount)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
                supplier_product_id=VALUES(supplier_product_id),
                item_name=VALUES(item_name),
                quantity=VALUES(quantity),
                unit_price=VALUES(unit_price),
                item_amount=VALUES(item_amount)
            """,
            [
                (
                    r["source_bill_id"],
                    r["source_item_index"],
                    r["supplier_product_id"],
                    r["item_name"],
                    parse_decimal(r["quantity"]),
                    parse_decimal(r["unit_price"]),
                    parse_decimal(r["item_amount"]),
                )
                for r in bill_items
            ],
        )

        connection.commit()
        print("MySQL load completed successfully.")

        for table in [
            "stg_users", "stg_orders", "order_items",
            "stg_bills", "bill_line_items"
        ]:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            print(f"{table}: {cursor.fetchone()[0]} rows")

    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    main()
