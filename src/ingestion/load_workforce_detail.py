
import csv
from pathlib import Path

from src.ingestion.db_connection import get_connection


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FILE_PATH = PROJECT_ROOT / "data" / "processed" / "workforce_detail.csv"


def collect_workforce_detail():
    if not FILE_PATH.is_file():
        raise FileNotFoundError(f"Missing file: {FILE_PATH.name}")

    records = []
    seen_keys = set()

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

        for row_number, row in enumerate(reader, start=2):
            if None in row or any(
                value is None for value in row.values()
            ):
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: invalid CSV row"
                )

            category = row.get("category")
            nationality = row.get("nationality")
            year_text = row.get("year")
            count_text = row.get("workforce_count")

            if not category or category != category.strip():
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: invalid category"
                )

            if not nationality or nationality != nationality.strip():
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: invalid nationality"
                )

            if nationality.casefold() == "total":
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: Total is not a nationality"
                )

            if not year_text or not year_text.isascii() or not year_text.isdigit():
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: invalid year"
                )

            year = int(year_text)

            if year <= 0 or year > 2147483647:
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: year out of range"
                )

            if not count_text or not count_text.isascii() or not count_text.isdigit():
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: invalid workforce count"
                )

            workforce_count = int(count_text)

            if workforce_count > 9223372036854775807:
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: count out of range"
                )

            key = (year, category, nationality)

            if key in seen_keys:
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: duplicate record"
                )

            seen_keys.add(key)

            records.append(
                (year, category, nationality, workforce_count)
            )

    if not records:
        raise ValueError(f"{FILE_PATH.name}: empty dataset")

    return records


def load_workforce_detail_to_db():
    records = collect_workforce_detail()
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("SELECT year FROM core.dim_year")
        valid_years = {row[0] for row in cursor.fetchall()}

        cursor.execute(
            "SELECT category_name, category_id "
            "FROM core.dim_workforce_category"
        )
        category_ids = {
            name: category_id
            for name, category_id in cursor.fetchall()
        }

        cursor.execute(
            "SELECT nationality_name, nationality_id "
            "FROM core.dim_nationality"
        )
        nationality_ids = {
            name: nationality_id
            for name, nationality_id in cursor.fetchall()
        }

        for year, category, nationality, workforce_count in records:
            if year not in valid_years:
                raise ValueError(
                    f"Year {year} is missing from core.dim_year"
                )

            if category not in category_ids:
                raise ValueError(
                    f"Category {category} is missing from "
                    "core.dim_workforce_category"
                )

            if nationality not in nationality_ids:
                raise ValueError(
                    f"Nationality {nationality} is missing from "
                    "core.dim_nationality"
                )

            cursor.execute(
                """
                INSERT INTO core.fact_workforce_detail (
                    year,
                    category_id,
                    nationality_id,
                    workforce_count,
                    source_file,
                    unit
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (year, category_id, nationality_id)
                DO UPDATE SET
                    workforce_count = EXCLUDED.workforce_count,
                    source_file = EXCLUDED.source_file,
                    unit = EXCLUDED.unit
                """,
                (
                    year,
                    category_ids[category],
                    nationality_ids[nationality],
                    workforce_count,
                    FILE_PATH.name,
                    "count",
                ),
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    return len(records)


if __name__ == "__main__":
    records = collect_workforce_detail()

    print("Validated records:", len(records))
    print("First 3 records:", records[:3])