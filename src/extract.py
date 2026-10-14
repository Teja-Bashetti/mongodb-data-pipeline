
<<<<<<< HEAD
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_DIR = BASE_DIR / "data" / "input"
RAW_DIR = BASE_DIR / "data" / "raw"
=======
"""
Extract Orders, Bills, and Users from MongoDB
or use the supplied JSON sample files.

Output:
data/raw/orders.json
data/raw/bills.json
data/raw/users.json
"""

import json
import os
from datetime import date, datetime
from pathlib import Path

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
INPUT_DIR = BASE_DIR / "data" / "input"
>>>>>>> origin/main

COLLECTIONS = ["orders", "bills", "users"]


<<<<<<< HEAD
def extract_collection(collection_name):
    input_path = INPUT_DIR / f"{collection_name}.json"
    output_path = RAW_DIR / f"{collection_name}.json"

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with input_path.open("r", encoding="utf-8") as file:
        records = json.load(file)

    if isinstance(records, dict):
        records = [records]

    if not isinstance(records, list):
        raise ValueError(
            f"{collection_name}.json must contain an object or list"
        )

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2, ensure_ascii=False)

    print(
        f"Extracted {len(records)} records "
        f"from {collection_name}"
    )


def main():
    for collection_name in COLLECTIONS:
        extract_collection(collection_name)

    print("Raw extraction completed successfully.")
=======
def json_serializer(value):
    """Convert MongoDB-specific values to JSON-compatible values."""
    if isinstance(value, ObjectId):
        return {"$oid": str(value)}
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    raise TypeError(f"Unsupported data type: {type(value).__name__}")


def save_json(records, output_path):
    """Write extracted documents to a JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            records,
            file,
            default=json_serializer,
            indent=2,
            ensure_ascii=False,
        )

    print(f"Saved {len(records)} records to {output_path}")


def extract_from_json():
    """Load the assignment's sample JSON files."""
    for collection in COLLECTIONS:
        input_path = INPUT_DIR / f"{collection}.json"

        if not input_path.exists():
            raise FileNotFoundError(
                f"Missing sample file: {input_path}. "
                "Place the downloaded JSON files in data/input/."
            )

        with input_path.open("r", encoding="utf-8") as file:
            documents = json.load(file)

        # Support either one JSON document or a list of documents.
        if isinstance(documents, dict):
            documents = [documents]

        if not isinstance(documents, list):
            raise ValueError(
                f"{collection}.json must contain a JSON object or array."
            )

        save_json(documents, RAW_DIR / f"{collection}.json")


def extract_from_mongodb():
    """Extract all three collections from MongoDB."""
    mongo_uri = os.getenv("MONGODB_URI")
    database_name = os.getenv("MONGODB_DATABASE")

    if not mongo_uri or not database_name:
        raise ValueError(
            "Set MONGODB_URI and MONGODB_DATABASE in your .env file."
        )

    client = MongoClient(
        mongo_uri,
        serverSelectionTimeoutMS=10000,
    )

    try:
        client.admin.command("ping")
        database = client[database_name]

        for collection_name in COLLECTIONS:
            collection = database[collection_name]
            documents = list(collection.find({}))

            save_json(
                documents,
                RAW_DIR / f"{collection_name}.json",
            )
    finally:
        client.close()


def main():
    source_mode = os.getenv("SOURCE_MODE", "json").lower()

    if source_mode == "json":
        extract_from_json()
    elif source_mode == "mongodb":
        extract_from_mongodb()
    else:
        raise ValueError(
            "SOURCE_MODE must be 'json' or 'mongodb'."
        )

    print("Extraction completed successfully.")
>>>>>>> origin/main


if __name__ == "__main__":
    main()
