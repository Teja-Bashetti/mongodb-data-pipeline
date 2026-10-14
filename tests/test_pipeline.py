
import json
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_DIR = BASE_DIR / "data" / "input"
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

COLLECTIONS = ["orders", "bills", "users"]


@pytest.mark.parametrize("collection", COLLECTIONS)
def test_input_file_exists(collection):
    """Check that each source JSON file exists."""
    file_path = INPUT_DIR / f"{collection}.json"
    assert file_path.exists(), f"Missing input file: {file_path}"


@pytest.mark.parametrize("collection", COLLECTIONS)
def test_input_json_is_valid(collection):
    """Check that each source file contains valid JSON."""
    file_path = INPUT_DIR / f"{collection}.json"

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    assert isinstance(data, (dict, list))
    assert len(data) > 0


@pytest.mark.parametrize("collection", COLLECTIONS)
def test_raw_json_is_valid(collection):
    """Check extracted raw data when available."""
    file_path = RAW_DIR / f"{collection}.json"

    if not file_path.exists():
        pytest.skip(f"Raw file not generated yet: {collection}")

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.parametrize(
    "filename",
    [
        "users.json",
        "orders.json",
        "order_items.json",
        "bills.json",
        "bill_line_items.json",
    ],
)
def test_processed_json_is_valid(filename):
    """Check transformed output files when available."""
    file_path = PROCESSED_DIR / filename

    if not file_path.exists():
        pytest.skip(f"Processed file not generated yet: {filename}")

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    assert isinstance(data, list)
