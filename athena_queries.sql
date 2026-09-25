# AWS Job Market ETL Pipeline

An end-to-end ETL pipeline that extracts data analyst job postings from the Adzuna API, cleans and transforms them in Python, uploads to AWS S3, and queries them with Amazon Athena.

---

##  Project Overview

A complete **cloud-based data engineering workflow**:

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
- **250 raw job postings extracted**

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
- Athena table reads directly from S3 using OpenCSVSerde
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

**Insight:** 90% of data analyst job postings in South Africa **do not disclose salary** — a significant transparency issue.

---

##  Key Findings

### 1. Salary Transparency Crisis
**90.3% of data analyst job postings do not disclose salary.** Only 20 out of 207 listings included salary information.

| Metric | Value |
|---|---|
| Jobs with salary data | 20 |
| Average salary | R409,284 |
| Minimum | R36 ⚠️ |
| Maximum | R1,140,000 |

**Data quality flag:** The minimum salary of R36 is clearly invalid — a real-world example of the noise in job market data.

### 2. Geographic Concentration
Johannesburg and Cape Town dominate the market:

| City | Jobs |
|---|---|
| Johannesburg | 71 |
| Cape Town Region | 60 |
| *(not specified)* | 27 |
| Tshwane (Pretoria) | 20 |
| Cape Winelands | 17 |
| Ekurhuleni | 4 |
| eThekwini (Durban) | 3 |

**Insight:** Johannesburg + Cape Town account for ~73% of all data analyst postings in South Africa.

### 3. Most In-Demand Skills

| Skill | Jobs mentioning it |
|---|---|
| **SQL** | **15** |
| **Excel** | **13** |
| **Power BI** | **12** |
| Tableau | 3 |
| Python | 1 |
| AWS | 0 |
| Azure | 0 |

**Insight:** SQL, Excel, and Power BI are the top 3 skills for data analysts in South Africa. Cloud skills are rarely mentioned in local postings but are increasingly valuable globally.

### 4. Top Employers (by volume)

| Company | Jobs |
|---|---|
| *(not specified)* | 34 |
| OfferZen (platform) | 33 |
| Hire Resolve | 9 |
| Network IT | 7 |
| Network Contracting Solutions | 4 |

**Data quality flag:** OfferZen is a **job board**, not a direct employer — its 33 listings come from multiple companies. This is a common trap in job market analysis.

### 5. Category Distribution

| Category | Jobs |
|---|---|
| IT | 166 |
| Accounting & Finance | 28 |
| Admin | 3 |
| Scientific & QA | 2 |
| Manufacturing | 2 |
| Graduate | 2 |

**Insight:** 80% of postings are tagged "IT" — expected for a data analyst search but reveals how coarse the category taxonomy is.

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

Run queries from athena_queries.sql in the AWS Athena console.


Skills Demonstrated
Python ETL: API extraction, data cleaning, transformation

pandas: data manipulation, deduplication, feature engineering

boto3: AWS SDK for S3 uploads

AWS S3: cloud storage, partitioned data

AWS Athena: serverless SQL on S3

AWS IAM: secure credential management

Data quality: null handling, deduplication, invalid data detection

SQL: analytical queries on cloud data


 Data Quality Observations
Real-world data is messy. This pipeline handles:

90.3% missing salary — most postings omit pay

17% duplicate rate — same jobs posted multiple times

Invalid salary values — a R36 minimum salary (clearly a test/error)

Job board vs employer confusion — OfferZen listings attributed as direct employer

Missing company names — 16.4% of postings hide the employer

Unicode escapes — \u2026 in descriptions

Nested JSON — company, location, and category are nested objects


 Contact
Portfolio: sandilenkosi12.github.io/DATA-ANALYST-PORTFOLIO

GitHub: github.com/sandilenkosi12

Email: abelnkosi2000@gmail.com


