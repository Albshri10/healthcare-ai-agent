
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.ingestion import (
    load_inpatients_by_sector,
    load_workforce_detail,
)


class TestIngestionValidation(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.file_path = Path(self.temp_dir.name) / "test.csv"

    def collect(self, module, function, csv_content):
        self.file_path.write_text(
            csv_content,
            encoding="utf-8"
        )

        with patch.object(module, "FILE_PATH", self.file_path):
            return function()

    def test_future_year_and_column_order(self):
        data = (
            "inpatient_count,year,sector\n"
            "123,2028,Future Sector\n"
        )

        records = self.collect(
            load_inpatients_by_sector,
            load_inpatients_by_sector.collect_inpatients_by_sector,
            data,
        )

        self.assertEqual(
            records,
            [(2028, "Future Sector", 123)]
        )

    def test_duplicate_inpatient_record(self):
        data = (
            "sector,year,inpatient_count\n"
            "MoH,2028,123\n"
            "MoH,2028,456\n"
        )

        with self.assertRaisesRegex(
            ValueError, "duplicate year and sector"
        ):
            self.collect(
                load_inpatients_by_sector,
                load_inpatients_by_sector.collect_inpatients_by_sector,
                data,
            )

    def test_negative_inpatient_count(self):
        data = (
            "sector,year,inpatient_count\n"
            "MoH,2028,-10\n"
        )

        with self.assertRaisesRegex(
            ValueError, "invalid inpatient count"
        ):
            self.collect(
                load_inpatients_by_sector,
                load_inpatients_by_sector.collect_inpatients_by_sector,
                data,
            )

    def test_missing_csv_value(self):
        data = (
            "sector,year,inpatient_count\n"
            "MoH,2028\n"
        )

        with self.assertRaisesRegex(
            ValueError, "invalid CSV row"
        ):
            self.collect(
                load_inpatients_by_sector,
                load_inpatients_by_sector.collect_inpatients_by_sector,
                data,
            )

    def test_duplicate_column_names(self):
        data = (
            "sector,year,year,inpatient_count\n"
            "MoH,2028,2028,123\n"
        )

        with self.assertRaisesRegex(
            ValueError, "duplicate column names"
        ):
            self.collect(
                load_inpatients_by_sector,
                load_inpatients_by_sector.collect_inpatients_by_sector,
                data,
            )

    def test_total_not_allowed_as_nationality(self):
        data = (
            "category,nationality,year,workforce_count\n"
            "Physicians,TOTAL,2028,100\n"
        )

        with self.assertRaisesRegex(
            ValueError, "Total is not a nationality"
        ):
            self.collect(
                load_workforce_detail,
                load_workforce_detail.collect_workforce_detail,
                data,
            )

    def test_future_workforce_record(self):
        data = (
            "workforce_count,nationality,category,year\n"
            "100,Saudi,Future Category,2028\n"
        )

        records = self.collect(
            load_workforce_detail,
            load_workforce_detail.collect_workforce_detail,
            data,
        )

        self.assertEqual(
            records,
            [(2028, "Future Category", "Saudi", 100)]
        )


if __name__ == "__main__":
    unittest.main()