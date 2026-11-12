
CREATE TABLE core.fact_workforce_detail (
    year INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    nationality_id INTEGER NOT NULL,
    workforce_count BIGINT NOT NULL,
    source_file TEXT NOT NULL,
    unit TEXT NOT NULL DEFAULT 'count',

    CONSTRAINT pk_fact_workforce_detail
        PRIMARY KEY (year, category_id, nationality_id),

    CONSTRAINT fk_workforce_year
        FOREIGN KEY (year)
        REFERENCES core.dim_year (year),

    CONSTRAINT fk_workforce_category
        FOREIGN KEY (category_id)
        REFERENCES core.dim_workforce_category (category_id),

    CONSTRAINT fk_workforce_nationality
        FOREIGN KEY (nationality_id)
        REFERENCES core.dim_nationality (nationality_id),

    CONSTRAINT chk_workforce_count_nonnegative
        CHECK (workforce_count >= 0),

    CONSTRAINT chk_workforce_source_valid
        CHECK (
            source_file = BTRIM(source_file)
            AND source_file <> ''
        ),

    CONSTRAINT chk_workforce_unit_valid
        CHECK (unit = 'count')
);