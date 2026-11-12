
from src.ingestion.load_years import (
    collect_years,
    load_years_to_db,
)
from src.ingestion.load_sectors import (
    collect_sectors,
    load_sectors_to_db,
)
from src.ingestion.load_workforce_categories import (
    collect_workforce_categories,
    load_workforce_categories_to_db,
)
from src.ingestion.load_nationalities import (
    collect_nationalities,
    load_nationalities_to_db,
)
from src.ingestion.load_inpatients_by_sector import (
    collect_inpatients_by_sector,
    load_inpatients_to_db,
)
from src.ingestion.load_inpatients_total import (
    collect_inpatients_total,
    load_inpatients_total_to_db,
)
from src.ingestion.load_inpatients_admission_rate import (
    collect_inpatients_admission_rate,
    load_inpatients_admission_rate_to_db,
)
from src.ingestion.load_workforce_detail import (
    collect_workforce_detail,
    load_workforce_detail_to_db,
)


def run_ingestion():
    validators = [
        ("Years", collect_years),
        ("Sectors", collect_sectors),
        ("Workforce categories", collect_workforce_categories),
        ("Nationalities", collect_nationalities),
        ("Inpatients by sector", collect_inpatients_by_sector),
        ("Inpatients total", collect_inpatients_total),
        ("Admission rates", collect_inpatients_admission_rate),
        ("Workforce detail", collect_workforce_detail),
    ]

    loaders = [
        ("Years", load_years_to_db),
        ("Sectors", load_sectors_to_db),
        ("Workforce categories", load_workforce_categories_to_db),
        ("Nationalities", load_nationalities_to_db),
        ("Inpatients by sector", load_inpatients_to_db),
        ("Inpatients total", load_inpatients_total_to_db),
        ("Admission rates", load_inpatients_admission_rate_to_db),
        ("Workforce detail", load_workforce_detail_to_db),
    ]

    print("Step 1: Validating processed data...")

    for name, validator in validators:
        records = validator()
        print(f"  {name}: {len(records)} validated")

    print("\nStep 2: Loading data into PostgreSQL...")

    for name, loader in loaders:
        result = loader()

        count = (
            len(result)
            if isinstance(result, list)
            else result
        )

        print(f"  {name}: {count} processed")

    print("\nIngestion completed successfully.")


if __name__ == "__main__":
    run_ingestion()