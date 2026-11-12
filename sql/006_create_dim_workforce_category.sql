
CREATE TABLE core.dim_workforce_category (
    category_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_name TEXT NOT NULL UNIQUE,

    CONSTRAINT chk_workforce_category_name_valid
        CHECK (
            category_name = BTRIM(category_name)
            AND category_name <> ''
        )
);