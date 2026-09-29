# AWS Job Market ETL Pipeline

An end-to-end ETL pipeline that extracts data analyst job postings from the Adzuna API, cleans and transforms them in Python, uploads to AWS S3, and queries them with Amazon Athena.

---

## Project Overview

This project demonstrates a complete **cloud-based data engineering workflow**:


Adzuna API → Python (extract + clean) → AWS S3 → Amazon Athena → SQL Insights

---

##  Stack

- **Python** — requests, pandas, boto3
- **AWS S3** — cloud storage
- **AWS Athena** — serverless SQL queries
- **AWS IAM** — secure credentials
- **Adzuna API** — live job market data

---

##  Project Structure

aws-etl-pipeline/
├── etl.py # Main ETL pipeline
├── requirements.txt # Python dependencies
├── .env # Credentials (not committed)
├── .gitignore # Excludes secrets
├── athena_queries.sql # All SQL queries
└── README.md

---

##  ETL Pipeline

### 1. Extract
- Fetches 5 pages × 50 results from Adzuna API (South Africa)
- Search term: `data analyst`
- 250 raw job postings extracted

### 2. Transform (8 cleaning steps)
1. **Salary normalisation** — handles nulls, zeros, type conversion
2. **Description cleaning** — removes unicode escapes, collapses whitespace
3. **Location flattening** — nested `area[]` → `country`, `province`, `city` columns
4. **Category standardisation** — "Accounting & Finance Jobs" → `accounting_finance`
5. **Company extraction** — nested object → simple string
6. **Date parsing** — ISO 8601 → datetime + `days_ago`
7. **Feature engineering** — `salary_avg`, `years_experience`
8. **Deduplication** — removes duplicates by title + company + city

### 3. Load
- Uploads cleaned CSV to `s3://sandile-job-market-etl/jobs/`
- File partitioned by date: `jobs_YYYYMMDD.csv`

### 4. Query
- Athena table reads directly from S3
- SQL queries answer business questions

---

##  Data Quality Report

| Metric | Value |
|---|---|
| Raw jobs extracted | 250 |
| Duplicates removed | 43 (17%) |
| Clean rows | 207 |
| **Missing salary** | **187 (90.3%)** |
| Missing company | 34 (16.4%) |
| Unique cities | 11 |
| Unique categories | 9 |

---

## Key Findings

### 1. Salary Transparency Crisis
**90.3% of data analyst job postings in South Africa do not disclose salary.**

This is a significant transparency issue for job seekers.

### 2. Top Hiring Cities
*(Insert top 5 cities from your query)*

![Uploading Screenshot 2026-09-24 165959.jpg…]()


### 3. Most In-Demand Skills

| Skill | Jobs mentioning it |
|---|---|
| **SQL** | 15 |
| **Excel** | 13 |
| **Power BI** | 12 |
| Tableau | 3 |
| Python | 1 |
| Azure | 0 |
| AWS | 0 |

**Insight:** SQL, Excel, and Power BI dominate the South African data analyst market. Cloud skills (AWS/Azure) are rarely mentioned in local postings but are increasingly valuable globally.

### 4. Top Hiring Companies
*(Insert top 5 companies from your query)*

---

##  How to Run

### 1. Clone and install
```bash
git clone https://github.com/sandilenkosi12/aws-etl-pipeline.git
cd aws-etl-pipeline
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

2. Configure .env
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=eu-north-1
S3_BUCKET=your_bucket_name

3. Run the pipeline
python etl.py

4. Query with Athena
Run athena_queries.sql in the AWS Athena console.

Skills Demonstrated
Python ETL: API extraction, data cleaning, transformation

pandas: data manipulation, deduplication, feature engineering

boto3: AWS SDK for S3 uploads

AWS S3: cloud storage, partitioned data

AWS Athena: serverless SQL on S3

AWS IAM: secure credential management

Data quality: null handling, deduplication, validation

SQL: analytical queries on cloud data


 Contact
Portfolio: sandilenkosi12.github.io/DATA-ANALYST-PORTFOLIO

GitHub: github.com/sandilenkosi12

Email: abelnkosi2000@gmail.com

