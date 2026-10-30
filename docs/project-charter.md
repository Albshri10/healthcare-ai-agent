# Project Charter

## Working project title

Healthcare AI Agent Project

The final public name will be selected after the system's identity and scope are
fully defined.

## Problem statement

Saudi healthcare data is distributed across multiple files and indicators.
Decision-makers need a consistent way to validate, combine, analyze, and
interpret these datasets. Static reports also become outdated when new yearly
data is released.

## Proposed solution

Build an extensible analytics and decision-support system that accepts approved
healthcare datasets, standardizes them, calculates transparent KPIs, generates
evaluated forecasts, and allows an AI agent to select trusted analytical tools
in response to user questions.

## Target users

- Healthcare data analysts
- Healthcare planners and decision-makers
- Researchers and students

## Core questions

1. How are healthcare workforce levels changing over time?
2. How is inpatient demand changing over time?
3. Is demand growing faster than workforce capacity?
4. Which healthcare clusters show capacity pressure?
5. What future trends are supported by the available data?
6. Which actions should decision-makers investigate based on transparent rules?

## In scope

- The eight supplied healthcare datasets
- Data quality checks and standardization
- SQL storage and queries
- Descriptive and diagnostic analysis
- Time-series forecasting with honest limitations
- Power BI and Streamlit dashboards
- AI-agent tool selection, explanations, memory, and guardrails
- Downloadable analytical reports

## Out of scope

- Medical diagnosis or treatment recommendations
- Autonomous operational decisions
- Modification of Ministry of Health systems
- Claims of self-learning without a verified learning mechanism
- Use of personal patient records

## Success criteria

- A new approved year can be added without rewriting analytical logic.
- Column order changes do not break ingestion.
- Invalid files fail with a clear explanation.
- Every KPI has a documented definition and source.
- Forecasts include evaluation metrics and limitations.
- The AI agent never invents a metric and identifies the tool and data used.
- A new developer can run the project using the README.

