
import csv
from pathlib import Path

from src.ingestion.db_connection import get_connection


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FILE_PATH = PROJECT_ROOT / "data" / "processed" / "inpatients_by_sector.csv"


def collect_inpatients_by_sector():
    if not FILE_PATH.is_file():
        raise FileNotFoundError(f"Missing file: {FILE_PATH.name}")

    records = []
    seen_keys = set()

    with FILE_PATH.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        columns = reader.fieldnames or []
        required = {"sector", "year", "inpatient_count"}

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

            sector = row.get("sector")
            year_text = row.get("year")
            count_text = row.get("inpatient_count")

            if not sector or not sector.strip():
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: invalid sector"
                )

            if sector != sector.strip():
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: extra sector spaces"
                )

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
                not count_text
                or not count_text.isascii()
                or not count_text.isdigit()
            ):
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: invalid inpatient count"
                )

            inpatient_count = int(count_text)

            if inpatient_count > 9223372036854775807:
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: count out of range"
                )

            key = (year, sector)

            if key in seen_keys:
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: duplicate year and sector"
                )

            seen_keys.add(key)

            records.append((year, sector, inpatient_count))

    if not records:
        raise ValueError(f"{FILE_PATH.name}: empty dataset")

    return records


def load_inpatients_to_db():
    records = collect_inpatients_by_sector()
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("SELECT year FROM core.dim_year")
        valid_years = {row[0] for row in cursor.fetchall()}

        cursor.execute(
            "SELECT sector_name, sector_id FROM core.dim_sector"
        )
        sector_ids = {
            name: sector_id
            for name, sector_id in cursor.fetchall()
        }

        for year, sector, inpatient_count in records:
            if year not in valid_years:
                raise ValueError(
                    f"Year {year} is missing from core.dim_year"
                )

            if sector not in sector_ids:
                raise ValueError(
                    f"Sector {sector} is missing from core.dim_sector"
                )

            cursor.execute(
                """
                INSERT INTO core.fact_inpatients_by_sector (
                    year,
                    sector_id,
                    inpatient_count,
                    source_file,
                    unit
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (year, sector_id)
                DO UPDATE SET
                    inpatient_count = EXCLUDED.inpatient_count,
                    source_file = EXCLUDED.source_file,
                    unit = EXCLUDED.unit
                """,
                (
                    year,
                    sector_ids[sector],
                    inpatient_count,
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
    records = collect_inpatients_by_sector()
    print("Validated records:", len(records))
    print("First 3 records:", records[:3])