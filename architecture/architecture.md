
# Data Pipeline Architecture

## Source to MySQL Data Warehouse

```mermaid
flowchart TD
    A[MongoDB Orders JSON]
    B[MongoDB Bills JSON]
    C[MongoDB Users JSON]

    A --> D[Extract - Python]
    B --> D
    C --> D

    D --> E[Raw JSON Files]
    E --> F[Validation]
    F --> G[Transformation - Python]
    G --> H[Processed JSON Files]

    H --> I[MySQL Loader]
    I --> J[Staging Tables]

    J --> K[STAR Schema]
    J --> L[SNOWFLAKE Schema]

    K --> M[Analytics and Reporting]
    L --> M
```

## Proposed Cloud Architecture

```mermaid
flowchart TD
    A[MongoDB Sources]
    A --> B[Zephyrus ELT Framework - Proposed]
    B --> C[Amazon S3]
    C --> D[AWS Glue and PySpark]
    D --> E[Amazon Redshift]
    E --> F[Analytics and Reporting]
```

**Note:** The local implementation uses Python and MySQL. The AWS diagram represents a proposed cloud architecture, not a deployed environment.
