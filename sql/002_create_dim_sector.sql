
CREATE TABLE core.dim_sector (
    sector_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sector_name TEXT NOT NULL UNIQUE,

    CONSTRAINT chk_sector_name_valid
        CHECK (
            sector_name = BTRIM(sector_name)
            AND sector_name <> ''
        )
);