
CREATE TABLE core.fact_inpatients_total (
    year INTEGER PRIMARY KEY,
    total_inpatients BIGINT NOT NULL,
    source_file TEXT NOT NULL,
    unit TEXT NOT NULL DEFAULT 'count',

    CONSTRAINT fk_inpatients_total_year
        FOREIGN KEY (year)
        REFERENCES core.dim_year (year),

    CONSTRAINT chk_total_inpatients_nonnegative
        CHECK (total_inpatients >= 0),

    CONSTRAINT chk_total_source_valid
        CHECK (
            source_file = BTRIM(source_file)
            AND source_file <> ''
        ),

    CONSTRAINT chk_total_unit_valid
        CHECK (unit = 'count')
);