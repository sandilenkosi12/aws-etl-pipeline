"""
Adzuna Job Market ETL Pipeline
==============================
Extracts data analyst job postings from the Adzuna API,
cleans and transforms them, then uploads to AWS S3.

Author: Sandile Nkosi
GitHub: github.com/sandilenkosi12
"""

import os
import re
import requests
import pandas as pd
import boto3
from datetime import datetime
from dotenv import load_dotenv

# ============================================
# CONFIG
# ============================================
load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")

COUNTRY = "za"
SEARCH_TERM = "data analyst"
MAX_PAGES = 5
RESULTS_PER_PAGE = 50
OUTPUT_FILE = f"jobs_{datetime.now().strftime('%Y%m%d')}.csv"
S3_KEY = f"jobs/jobs_{datetime.now().strftime('%Y%m%d')}.csv"


# ============================================
# 1. EXTRACT
# ============================================
def extract():
    """Fetch job postings from Adzuna API across multiple pages."""
    all_jobs = []
    for page in range(1, MAX_PAGES + 1):
        url = f"https://api.adzuna.com/v1/api/jobs/{COUNTRY}/search/{page}"
        params = {
            "app_id": APP_ID,
            "app_key": APP_KEY,
            "results_per_page": RESULTS_PER_PAGE,
            "what": SEARCH_TERM,
            "content-type": "application/json"
        }
        print(f"Fetching page {page}...")
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        all_jobs.extend(data.get("results", []))

    print(f"Extracted {len(all_jobs)} raw job postings.")
    return all_jobs


# ============================================
# 2. CLEANING FUNCTIONS
# ============================================
def clean_salary(value):
    """Convert salary values to numeric, handle nulls and zeros."""
    if value is None or value == "" or value == 0:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def clean_description(text):
    """Remove unicode escapes and collapse whitespace in description."""
    if not text:
        return ""
    text = text.replace("\u2026", "...").replace("\u2019", "'")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_location(location_obj):
    """Extract structured location from nested object."""
    if not location_obj:
        return {"city": None, "province": None, "country": None, "display": None}
    area = location_obj.get("area", [])
    return {
        "country": area[0] if len(area) > 0 else None,
        "province": area[1] if len(area) > 1 else None,
        "city": area[2] if len(area) > 2 else None,
        "display": location_obj.get("display_name")
    }


def clean_category(category_obj):
    """Standardise category label into snake_case."""
    if not category_obj:
        return None
    label = category_obj.get("label", "")
    cleaned = label.lower().replace(" jobs", "").replace(" & ", "_").replace(" ", "_")
    return cleaned


def clean_company(company_obj):
    """Extract company display name from nested object."""
    if not company_obj:
        return None
    return company_obj.get("display_name")


def parse_salary_flag(value):
    """Convert salary_is_predicted string to boolean."""
    return value == "1"


def extract_years_experience(text):
    """Extract years of experience mentioned in description."""
    if not text:
        return None
    match = re.search(r"(\d+)\+?\s*(?:years|yrs)", text.lower())
    return int(match.group(1)) if match else None


# ============================================
# 3. TRANSFORM
# ============================================
def transform(raw_jobs):
    """Flatten nested JSON, clean fields, deduplicate, add derived columns."""
    cleaned = []

    for job in raw_jobs:
        loc = clean_location(job.get("location"))
        record = {
            "job_id": job.get("id"),
            "title": job.get("title", "").strip(),
            "company": clean_company(job.get("company")),
            "category": clean_category(job.get("category")),
            "contract_type": job.get("contract_type"),
            "salary_min": clean_salary(job.get("salary_min")),
            "salary_max": clean_salary(job.get("salary_max")),
            "salary_is_predicted": parse_salary_flag(job.get("salary_is_predicted")),
            "country": loc["country"],
            "province": loc["province"],
            "city": loc["city"],
            "location_display": loc["display"],
            "latitude": job.get("latitude"),
            "longitude": job.get("longitude"),
            "description": clean_description(job.get("description")),
            "created_at": job.get("created"),
            "redirect_url": job.get("redirect_url")
        }
        cleaned.append(record)

    df = pd.DataFrame(cleaned)

    # Parse date
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["created_date"] = df["created_at"].dt.date
    df["days_ago"] = (pd.Timestamp.now(tz="UTC") - df["created_at"]).dt.days

    # Compute average salary
    df["salary_avg"] = df[["salary_min", "salary_max"]].mean(axis=1)

    # Extract years of experience
    df["years_experience"] = df["description"].apply(extract_years_experience)

    # Deduplicate by title + company + city
    before = len(df)
    df = df.drop_duplicates(subset=["title", "company", "city"], keep="first")
    after = len(df)
    print(f"Deduplicated: {before} -> {after} rows ({before - after} removed)")

    # Sort by newest
    df = df.sort_values("created_at", ascending=False).reset_index(drop=True)

    print(f"Transformed {len(df)} rows with {len(df.columns)} columns.")
    return df


# ============================================
# 4. LOAD
# ============================================
def load_local(df, filename):
    """Save cleaned data to CSV locally."""
    df.to_csv(filename, index=False)
    print(f"Saved locally to {filename}")


def load_to_s3(df, bucket, key):
    """Upload dataframe as CSV to S3."""
    print(f"Uploading to s3://{bucket}/{key} ...")
    s3 = boto3.client(
        "s3",
        region_name=AWS_REGION,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    csv_data = df.to_csv(index=False)
    s3.put_object(Bucket=bucket, Key=key, Body=csv_data)
    print("Upload complete.")


# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    print("=" * 60)
    print("ADZUNA JOB MARKET ETL PIPELINE")
    print("=" * 60)

    raw = extract()
    df = transform(raw)
    load_local(df, OUTPUT_FILE)
    load_to_s3(df, S3_BUCKET, S3_KEY)

    print("\n--- SAMPLE OUTPUT ---")
    print(df[["title", "company", "city", "salary_avg", "days_ago"]].head(10))

    print("\n--- DATA QUALITY REPORT ---")
    print(f"Total jobs: {len(df)}")
    print(f"Missing salary: {df['salary_avg'].isna().sum()} ({df['salary_avg'].isna().mean():.1%})")
    print(f"Missing company: {df['company'].isna().sum()}")
    print(f"Unique cities: {df['city'].nunique()}")
    print(f"Unique categories: {df['category'].nunique()}")