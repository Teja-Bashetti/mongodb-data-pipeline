# mongodb-data-pipeline
Production-ready MongoDB to PostgreSQL and Redshift data pipeline

mongodb-data-pipeline/
│
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── architecture/
│   └── architecture.mmd
│
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── validate.py
│   ├── load.py
│   └── main.py
│
├── sql/
│   ├── normalized_schema.sql
│   ├── star_schema.sql
│   └── snowflake_schema.sql
│
├── schemas/
│   ├── star_schema.mmd
│   └── snowflake_schema.mmd
│
└── tests/
    └── test_pipeline.py
