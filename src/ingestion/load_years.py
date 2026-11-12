
import csv
from pathlib import Path

from src.ingestion.db_connection import get_connection


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

EXPECTED_FILES = [
    "inpatients_admission_rate.csv",
    "inpatients_by_sector.csv",
    "inpatients_total.csv",
    "workforce_category_totals.csv",
    "workforce_combined_categories.csv",
    "workforce_detail.csv",
]


def collect_years():
    years = set()

    for filename in EXPECTED_FILES:
        file_path = PROCESSED_DIR / filename

        if not file_path.is_file():
            raise FileNotFoundError(
                f"Missing file: {filename}"
            )

        with file_path.open(
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)
            columns = reader.fieldnames or []

            if len(columns) != len(set(columns)):
                raise ValueError(
                    f"{filename}: duplicate column names"
                )

            if "year" not in columns:
                raise ValueError(
                    f"{filename}: missing year column"
                )

            row_count = 0

            for row_number, row in enumerate(reader, start=2):
                if None in row or any(
                    value is None for value in row.values()
                ):
                    raise ValueError(
                        f"{filename}, row {row_number}: invalid CSV row"
                    )

                value = row.get("year")

                if (
                    not value
                    or not value.isascii()
                    or not value.isdigit()
                ):
                    raise ValueError(
                        f"{filename}, row {row_number}: invalid year"
                    )

                year = int(value)

                if year <= 0 or year > 2147483647:
                    raise ValueError(
                        f"{filename}, row {row_number}: year out of range"
                    )

                years.add(year)
                row_count += 1

            if row_count == 0:
                raise ValueError(
                    f"{filename}: empty dataset"
                )

    return sorted(years)


def load_years_to_db():
    years = collect_years()
    conn = get_connection()

    try:
        cursor = conn.cursor()

        for year in years:
            cursor.execute(
                """
                INSERT INTO core.dim_year (year)
                VALUES (%s)
                ON CONFLICT (year) DO NOTHING
                """,
                (year,),
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    return years


if __name__ == "__main__":
    print("Validated years:", collect_years())