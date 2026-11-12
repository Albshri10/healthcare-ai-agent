
import csv
from pathlib import Path

from src.ingestion.db_connection import get_connection


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FILE_PATH = PROJECT_ROOT / "data" / "processed" / "workforce_detail.csv"


def collect_workforce_categories():
    if not FILE_PATH.is_file():
        raise FileNotFoundError(f"Missing file: {FILE_PATH.name}")

    categories = set()

    with FILE_PATH.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        columns = reader.fieldnames or []
        required = {
            "category",
            "nationality",
            "year",
            "workforce_count",
        }

        if len(columns) != len(set(columns)):
            raise ValueError(
                f"{FILE_PATH.name}: duplicate column names"
            )

        missing = required - set(columns)

        if missing:
            raise ValueError(
                f"{FILE_PATH.name}: missing columns: {sorted(missing)}"
            )

        row_count = 0

        for row_number, row in enumerate(reader, start=2):
            if None in row or any(
                value is None for value in row.values()
            ):
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: invalid CSV row"
                )

            category = row.get("category")

            if not category or not category.strip():
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: invalid category"
                )

            if category != category.strip():
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: extra category spaces"
                )

            categories.add(category)
            row_count += 1

        if row_count == 0:
            raise ValueError(f"{FILE_PATH.name}: empty dataset")

    return sorted(categories)


def load_workforce_categories_to_db():
    categories = collect_workforce_categories()
    conn = get_connection()

    try:
        cursor = conn.cursor()

        for category in categories:
            cursor.execute(
                """
                INSERT INTO core.dim_workforce_category (
                    category_name
                )
                VALUES (%s)
                ON CONFLICT (category_name) DO NOTHING
                """,
                (category,),
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    return categories


if __name__ == "__main__":
    print(
        "Validated categories:",
        collect_workforce_categories()
    )