# Data Design Principles

## 1. Preserve raw data

Original CSV and Excel files are stored unchanged in `data/raw`. All cleaning
creates new data in later layers.

## 2. Use long-format analytical tables

Source format:

```text
Category | 2020G | 2021G | 2022G | 2023G | 2024G
```

Standard internal format:

```text
year | category | value | unit | source
```

This allows 2025–2030 data to be appended as rows without changing the program.

## 3. Depend on meaning, not column position

The pipeline identifies fields by approved names and aliases. Reordering
columns is allowed; missing or ambiguous required fields are rejected.

## 4. Validate before loading

Each dataset will have a data contract defining:

- Required fields
- Accepted aliases
- Data types
- Units
- Allowed missing values
- Uniqueness rules
- Valid ranges
- Source and update frequency

## 5. Separate source adapters from the standard schema

If a future file uses different labels, a source-specific adapter maps it to
the standard schema. Analytical code reads only the standard schema.

## 6. Make changes traceable

Every load records the source filename, load time, validation result, and
transformation version.

