
CREATE TABLE core.fact_inpatients_admission_rate (
    year INTEGER PRIMARY KEY,
    admissions_per_100 NUMERIC NOT NULL,
    source_file TEXT NOT NULL,
    unit TEXT NOT NULL DEFAULT 'admissions_per_100_persons',

    CONSTRAINT fk_admission_rate_year
        FOREIGN KEY (year)
        REFERENCES core.dim_year (year),

    CONSTRAINT chk_admission_rate_nonnegative
        CHECK (admissions_per_100 >= 0),

    CONSTRAINT chk_admission_rate_source_valid
        CHECK (
            source_file = BTRIM(source_file)
            AND source_file <> ''
        ),

    CONSTRAINT chk_admission_rate_unit_valid
        CHECK (unit = 'admissions_per_100_persons')
);