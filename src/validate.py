
<<<<<<< HEAD
=======
"""Validate extracted Orders, Bills, and Users JSON documents."""

>>>>>>> origin/main
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"

<<<<<<< HEAD
COLLECTIONS = ["orders", "bills", "users"]


def get_source_id(record):
    source_id = record.get("_id")

    # MongoDB Extended JSON format: {"$oid": "..."}
    if isinstance(source_id, dict):
        return source_id.get("$oid")

    # Also support string IDs
    return source_id


def validate_collection(name):
    file_path = RAW_DIR / f"{name}.json"

    if not file_path.exists():
        raise FileNotFoundError(
            f"Raw file not found: {file_path}. Run extract.py first."
        )

    with file_path.open("r", encoding="utf-8") as file:
        records = json.load(file)
=======
COLLECTIONS = ("orders", "bills", "users")


def get_source_id(document):
    """Read MongoDB ObjectId from common JSON representations."""
    value = document.get("_id")

    if isinstance(value, dict):
        return value.get("$oid")

    if isinstance(value, str):
        return value

    return None


def validate_collection(collection_name):
    """Return validation errors and record counts for one collection."""
    file_path = RAW_DIR / f"{collection_name}.json"

    if not file_path.exists():
        return {
            "collection": collection_name,
            "count": 0,
            "errors": [f"File not found: {file_path}"],
        }

    with file_path.open("r", encoding="utf-8") as file:
        documents = json.load(file)

    if not isinstance(documents, list):
        return {
            "collection": collection_name,
            "count": 0,
            "errors": ["Expected a JSON array of documents."],
        }
>>>>>>> origin/main

    errors = []
    seen_ids = set()

<<<<<<< HEAD
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"Record {index}: expected a JSON object")
            continue

        source_id = get_source_id(record)

        if not source_id:
            errors.append(f"Record {index}: missing source ID")
        elif source_id in seen_ids:
            errors.append(
                f"Record {index}: duplicate source ID {source_id}"
            )
        else:
            seen_ids.add(source_id)

        if name == "orders":
            products = record.get("products", [])

            if not isinstance(products, list):
                errors.append(
                    f"Record {index}: products must be an array"
                )

        elif name == "bills":
            line_items = record.get("line_items", [])

            if not isinstance(line_items, list):
                errors.append(
                    f"Record {index}: line_items must be an array"
                )

        elif name == "users":
            user_types = record.get("user_type")

            if user_types is not None and not isinstance(user_types, list):
                errors.append(
                    f"Record {index}: user_type must be an array when present"
                )

    print(f"\n{name.upper()}")
    print(f"Records checked: {len(records)}")
    print(f"Unique IDs: {len(seen_ids)}")
    print(f"Validation errors: {len(errors)}")

    for error in errors:
        print("ERROR:", error)

    return errors


def main():
    all_errors = []

    for name in COLLECTIONS:
        all_errors.extend(validate_collection(name))

    if all_errors:
        print("\nValidation completed with errors.")
        raise SystemExit(1)

    print("\nAll validation checks passed.")
=======
    for index, document in enumerate(documents):
        if not isinstance(document, dict):
            errors.append(f"Record {index}: document must be an object.")
            continue

        source_id = get_source_id(document)

        if not source_id:
            errors.append(f"Record {index}: missing MongoDB _id.$oid.")

        elif source_id in seen_ids:
            errors.append(
                f"Record {index}: duplicate source ID {source_id}."
            )

        else:
            seen_ids.add(source_id)

        # Validate known nested arrays when present.
        nested_fields = {
            "orders": ("products",),
            "bills": ("line_items", "items"),
            "users": (),
        }

        for field in nested_fields[collection_name]:
            if field in document and document[field] is not None:
                if not isinstance(document[field], list):
                    errors.append(
                        f"Record {index}: '{field}' must be an array."
                    )

    return {
        "collection": collection_name,
        "count": len(documents),
        "errors": errors,
    }


def main():
    all_valid = True

    for collection in COLLECTIONS:
        result = validate_collection(collection)

        print(
            f"\n{result['collection']}: "
            f"{result['count']} records"
        )

        if result["errors"]:
            all_valid = False
            for error in result["errors"]:
                print(f"  ERROR: {error}")
        else:
            print("  Validation passed.")

    if not all_valid:
        raise SystemExit("Validation failed. Review the errors above.")

    print("\nAll collections passed validation.")
>>>>>>> origin/main


if __name__ == "__main__":
    main()
