
import csv
from pathlib import Path

from src.ingestion.db_connection import get_connection


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FILE_PATH = PROJECT_ROOT / "data" / "processed" / "workforce_detail.csv"


def collect_nationalities():
    if not FILE_PATH.is_file():
        raise FileNotFoundError(f"Missing file: {FILE_PATH.name}")

    nationalities = set()

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

            nationality = row.get("nationality")

            if not nationality or not nationality.strip():
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: invalid nationality"
                )

            if nationality != nationality.strip():
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: extra nationality spaces"
                )

            if nationality.casefold() == "total":
                raise ValueError(
                    f"{FILE_PATH.name}, row {row_number}: Total is not a nationality"
                )

            nationalities.add(nationality)
            row_count += 1

        if row_count == 0:
            raise ValueError(f"{FILE_PATH.name}: empty dataset")

    return sorted(nationalities)


def load_nationalities_to_db():
    nationalities = collect_nationalities()
    conn = get_connection()

    try:
        cursor = conn.cursor()

        for nationality in nationalities:
            cursor.execute(
                """
                INSERT INTO core.dim_nationality (
                    nationality_name
                )
                VALUES (%s)
                ON CONFLICT (nationality_name) DO NOTHING
                """,
                (nationality,),
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    return nationalities


if __name__ == "__main__":
    print("Validated nationalities:", collect_nationalities())