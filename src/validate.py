
"""Validate extracted Orders, Bills, and Users JSON documents."""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"

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

    errors = []
    seen_ids = set()

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


if __name__ == "__main__":
    main()
