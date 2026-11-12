
CREATE TABLE core.fact_inpatients_by_sector (
    year INTEGER NOT NULL,
    sector_id INTEGER NOT NULL,
    inpatient_count BIGINT NOT NULL,
    source_file TEXT NOT NULL,
    unit TEXT NOT NULL DEFAULT 'count',

    CONSTRAINT pk_fact_inpatients_by_sector
        PRIMARY KEY (year, sector_id),

    CONSTRAINT fk_inpatients_year
        FOREIGN KEY (year)
        REFERENCES core.dim_year (year),

    CONSTRAINT fk_inpatients_sector
        FOREIGN KEY (sector_id)
        REFERENCES core.dim_sector (sector_id),

    CONSTRAINT chk_inpatient_count_nonnegative
        CHECK (inpatient_count >= 0),

    CONSTRAINT chk_inpatient_source_valid
        CHECK (
            source_file = BTRIM(source_file)
            AND source_file <> ''
        ),

    CONSTRAINT chk_inpatient_unit_valid
        CHECK (
            unit = BTRIM(unit)
            AND unit <> ''
        )
);