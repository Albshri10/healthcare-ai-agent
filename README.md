# Healthcare AI Agent Project

> Working title. The final project name will be selected later.

An extensible healthcare analytics and decision-support project that combines
data engineering, exploratory data analysis, forecasting, dashboards, and an
AI agent capable of selecting trusted analytical tools.

## Project goals

- Ingest healthcare data from CSV and Excel files.
- Validate and standardize incoming datasets.
- Store clean data in a relational database.
- Analyze healthcare workforce, inpatient demand, hospital activity, and capacity.
- Build transparent forecasts and evaluate their accuracy.
- Publish interactive Power BI and Streamlit dashboards.
- Build an AI agent that selects analytical tools based on the user's goal.
- Keep every result traceable to its data source and calculation.

## Scalability principles

1. New years are added as rows, not hard-coded as new program logic.
2. Column order does not matter; validated column names and meanings do.
3. Different source formats are converted into one standard internal schema.
4. Raw data is never modified.
5. Cleaning, analysis, forecasting, and presentation remain separate layers.
6. Models are retrained and evaluated when approved new data is added.
7. The AI agent can use only registered, tested analytical tools.

## Planned outputs

- Jupyter notebooks for learning and exploration
- Reusable Python modules
- SQL database and analysis queries
- Power BI dashboard
- Streamlit web application
- Forecasting models and evaluation report
- AI agent with tools, memory, and guardrails
- Documentation suitable for GitHub and LinkedIn

## Project structure

```text
healthcare-ai-agent/
├── data/
│   ├── raw/               # Original source files (never edited)
│   ├── interim/           # Standardized intermediate data
│   └── processed/         # Analysis-ready data
├── docs/                  # Project decisions and data documentation
├── notebooks/             # Step-by-step learning and exploration
├── sql/                   # Database schema and analytical queries
├── src/
│   ├── ingestion/         # File reading and source adapters
│   ├── validation/        # Schema and data-quality checks
│   ├── transformation/    # Cleaning and standardization
│   ├── analytics/         # KPIs and statistical analysis
│   ├── forecasting/       # Models and evaluation
│   ├── agent/             # Agent tools, planning, memory, guardrails
│   └── reporting/         # Reports and exports
├── dashboard/             # Power BI documentation/assets
├── app/                   # Streamlit interface
├── tests/                 # Automated tests
├── .gitignore
├── requirements.txt
└── README.md
```

## Current status

- [x] Project scope defined
- [x] Extensible architecture selected
- [ ] Development environment verified
- [ ] Eight source datasets audited
- [ ] Data contracts created
- [ ] Database designed
- [ ] Data pipeline implemented
- [ ] Analysis and KPIs completed
- [ ] Forecasting completed
- [ ] Dashboards completed
- [ ] AI agent completed
- [ ] Testing and documentation completed

