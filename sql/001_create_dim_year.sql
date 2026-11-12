CREATE TABLE core.dim_year (
    year INTEGER PRIMARY KEY,
    CONSTRAINT chk_year_positive CHECK (year > 0)
);