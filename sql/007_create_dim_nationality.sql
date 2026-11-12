
CREATE TABLE core.dim_nationality (
    nationality_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nationality_name TEXT NOT NULL UNIQUE,

    CONSTRAINT chk_nationality_name_valid
        CHECK (
            nationality_name = BTRIM(nationality_name)
            AND nationality_name <> ''
            AND nationality_name <> 'Total'
        )
);