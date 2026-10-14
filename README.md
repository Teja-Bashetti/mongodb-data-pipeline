# MongoDB Data Pipeline

## Career Objective

Deploy a reliable and scalable data pipeline to extract data from MongoDB JSON sources, validate and transform the data using Python, and load it into a MySQL data warehouse for analytical reporting. The project demonstrates ETL concepts, data quality validation, and STAR and SNOWFLAKE schema designs.

## Project Overview

This project processes sample Users, Orders, and Bills JSON data. It extracts source files, validates their structure, transforms nested records into relational datasets, and loads the results into MySQL staging and warehouse tables.

## Technology Stack

- Python
- JSON
- MySQL
- SQL
- Pytest
- Git and GitHub
- Zephyrus ELT — considered as a hypothetical framework for the proposed architecture, not an implemented dependency

## Pipeline Workflow

1. Extract Users, Orders, and Bills JSON files.
2. Validate source data and record identifiers.
3. Transform nested JSON records into relational datasets.
4. Load transformed data into MySQL staging tables.
5. Populate STAR and SNOWFLAKE warehouse schemas.
6. Run tests and SQL queries to validate the pipeline.

## Data Warehouse Design

### STAR Schema

Uses dimension tables such as users, products, and dates alongside order and order-item fact tables. Bill-related fact and supplier tables are also included.

### SNOWFLAKE Schema

Normalizes selected dimensions, including location and product/supplier information, to reduce repeated descriptive data.

The STAR schema is generally simpler for analytical queries, while the SNOWFLAKE schema provides additional normalization.

## Project Structure

- `data/input/` — sample source JSON files
- `src/` — extraction, inspection, validation, transformation, and loading scripts
- `sql/` — STAR and SNOWFLAKE schema and load scripts
- `architecture/` — pipeline architecture documentation
- `tests/` — automated tests
- `.gitignore` — excludes environment files and generated data

## Assumptions and Limitations

- The supplied JSON files are sample inputs and may contain only a small number of source documents.
- MySQL is the implemented relational destination.
- AWS Glue, Amazon S3, and Amazon Redshift are potential components of a future cloud deployment; this local project does not claim they have been deployed.
- Zephyrus ELT is a hypothetical framework used for architectural discussion.
- Production-scale scheduling, retries, and monitoring would require additional implementation.

## How to Run

1. Create and activate a Python virtual environment.
2. Install dependencies using `pip install -r requirements.txt`.
3. Place the source JSON files in `data/input/`.
4. Run the extraction, validation, and transformation scripts in the appropriate order.
5. Configure MySQL credentials locally using a `.env` file.
6. Execute the SQL schema and load scripts in MySQL Workbench.
7. Run tests using `pytest -v`.

## Security

Never commit `.env` files, passwords, database credentials, or other secrets to GitHub.