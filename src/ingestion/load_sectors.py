
import csv
from pathlib import Path

from src.ingestion.db_connection import get_connection


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FILE_PATH = PROJECT_ROOT / "data" / "processed" / "inpatients_by_sector.csv"


def collect_sectors():
    if not FILE_PATH.is_file():
        raise FileNotFoundError(
            f"Missing file: {FILE_PATH.name}"
        )

    sectors = set()

    with FILE_PATH.open(
        encoding="utf-8-sig",
        newline=""
    ) as file:

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

        row_count = 0

        for row_number, row in enumerate(reader, start=2):
            if None in row or any(
                value is None for value in row.values()
            ):
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: invalid CSV row"
                )

            sector = row.get("sector")

            if not sector or not sector.strip():
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: invalid sector"
                )

            if sector != sector.strip():
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: extra spaces in sector"
                )

            sectors.add(sector)
            row_count += 1

        if row_count == 0:
            raise ValueError(
                f"{FILE_PATH.name}: empty dataset"
            )

    return sorted(sectors)


def load_sectors_to_db():
    sectors = collect_sectors()
    conn = get_connection()

    try:
        cursor = conn.cursor()

        for sector in sectors:
            cursor.execute(
                """
                INSERT INTO core.dim_sector (sector_name)
                VALUES (%s)
                ON CONFLICT (sector_name) DO NOTHING
                """,
                (sector,),
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    return sectors


if __name__ == "__main__":
    print("Validated sectors:", collect_sectors())