
import csv
import re
from decimal import Decimal
from pathlib import Path

from src.ingestion.db_connection import get_connection


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FILE_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "inpatients_admission_rate.csv"
)


def collect_inpatients_admission_rate():
    if not FILE_PATH.is_file():
        raise FileNotFoundError(
            f"Missing file: {FILE_PATH.name}"
        )

    records = []
    seen_years = set()

    with FILE_PATH.open(
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        columns = reader.fieldnames or []
        required = {"year", "admissions_per_100"}

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
            rate_text = row.get("admissions_per_100")

            if not year_text or not re.fullmatch(
                r"[0-9]+", year_text
            ):
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: invalid year"
                )

            year = int(year_text)

            if year <= 0 or year > 2147483647:
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: year out of range"
                )

            if not rate_text or not re.fullmatch(
                r"[0-9]+(?:\.[0-9]+)?",
                rate_text
            ):
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: invalid admission rate"
                )

            admissions_per_100 = Decimal(rate_text)

            if year in seen_years:
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: duplicate year"
                )

            seen_years.add(year)

            records.append(
                (year, admissions_per_100)
            )

    if not records:
        raise ValueError(
            f"{FILE_PATH.name}: empty dataset"
        )

    return records


def load_inpatients_admission_rate_to_db():
    records = collect_inpatients_admission_rate()
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("SELECT year FROM core.dim_year")
        valid_years = {row[0] for row in cursor.fetchall()}

        for year, admissions_per_100 in records:
            if year not in valid_years:
                raise ValueError(
                    f"Year {year} is missing from core.dim_year"
                )

            cursor.execute(
                """
                INSERT INTO core.fact_inpatients_admission_rate (
                    year,
                    admissions_per_100,
                    source_file,
                    unit
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (year)
                DO UPDATE SET
                    admissions_per_100 = EXCLUDED.admissions_per_100,
                    source_file = EXCLUDED.source_file,
                    unit = EXCLUDED.unit
                """,
                (
                    year,
                    admissions_per_100,
                    FILE_PATH.name,
                    "admissions_per_100_persons",
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
    records = collect_inpatients_admission_rate()

    print("Validated records:", len(records))
    print("Records:", records)