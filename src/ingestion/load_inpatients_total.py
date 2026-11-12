
import csv
from pathlib import Path

from src.ingestion.db_connection import get_connection


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FILE_PATH = PROJECT_ROOT / "data" / "processed" / "inpatients_total.csv"


def collect_inpatients_total():
    if not FILE_PATH.is_file():
        raise FileNotFoundError(f"Missing file: {FILE_PATH.name}")

    records = []
    seen_years = set()

    with FILE_PATH.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        columns = reader.fieldnames or []
        required = {"year", "total_inpatients"}

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

            year_text = row.get("year")
            total_text = row.get("total_inpatients")

            if (
                not year_text
                or not year_text.isascii()
                or not year_text.isdigit()
            ):
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: invalid year"
                )

            year = int(year_text)

            if year <= 0 or year > 2147483647:
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: year out of range"
                )

            if (
                not total_text
                or not total_text.isascii()
                or not total_text.isdigit()
            ):
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: invalid total"
                )

            total_inpatients = int(total_text)

            if total_inpatients > 9223372036854775807:
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: total out of range"
                )

            if year in seen_years:
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: duplicate year"
                )

            seen_years.add(year)
            records.append((year, total_inpatients))

    if not records:
        raise ValueError(f"{FILE_PATH.name}: empty dataset")

    return records


def load_inpatients_total_to_db():
    records = collect_inpatients_total()
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("SELECT year FROM core.dim_year")
        valid_years = {row[0] for row in cursor.fetchall()}

        for year, total_inpatients in records:
            if year not in valid_years:
                raise ValueError(
                    f"Year {year} is missing from core.dim_year"
                )

            cursor.execute(
                """
                INSERT INTO core.fact_inpatients_total (
                    year,
                    total_inpatients,
                    source_file,
                    unit
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (year)
                DO UPDATE SET
                    total_inpatients = EXCLUDED.total_inpatients,
                    source_file = EXCLUDED.source_file,
                    unit = EXCLUDED.unit
                """,
                (
                    year,
                    total_inpatients,
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
    records = collect_inpatients_total()

    print("Validated records:", len(records))
    print("Records:", records)