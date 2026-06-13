# MarketPulse — Financial News Intelligence Pipeline

> **Does pre-earnings news sentiment predict whether a company beats its revenue estimate?**

This project builds an end-to-end data pipeline to answer that question empirically. It ingests live financial news and earnings data daily, applies NLP sentiment scoring, and structures everything into an analytics-ready warehouse for analysis.

---

## The Problem

Earnings surprises move markets. But the signals that predict them — news coverage, analyst tone, media sentiment — are unstructured and scattered. This pipeline turns that raw signal into structured, queryable data.

The core question: if you track news sentiment about a company in the 30 days before their earnings report, does the sentiment pattern differ between companies that beat estimates and those that miss?

---

## Architecture

```
NewsAPI + Alpha Vantage
        │
        ▼
Python Ingestion Scripts
(idempotent MERGE upserts)
        │
        ▼
Snowflake — RAW schema
        │
        ▼
dbt Transformations (3 layers)
├── Staging    → clean, type-cast raw data
├── Intermediate → join news + earnings, apply FinBERT sentiment scoring
└── Mart       → mart_company_sentiment
               → mart_earnings_vs_sentiment
               → mart_news_signals
        │
        ▼
Apache Airflow DAGs
(daily schedule, retries, Slack alerts on failure)
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Ingestion | Python, NewsAPI, Alpha Vantage API |
| Storage | Snowflake |
| Transformation | dbt Core |
| Orchestration | Apache Airflow |
| NLP / Sentiment | FinBERT (HuggingFace Transformers) |
| Language | Python (Pandas, NumPy) |

---

## Companies Tracked

AAPL, MSFT, GOOGL, AMZN, META, TSLA, JPM, GS, NFLX, NVDA

---

## Key Engineering Decisions

**Idempotent ingestion** — MERGE upserts instead of INSERT so the pipeline can safely rerun without creating duplicate records.

**3-layer dbt architecture** — raw data is never modified. Staging cleans it. Intermediate applies business logic and sentiment scoring. Mart tables are the final analytics-ready output.

**FinBERT for sentiment** — general-purpose sentiment models perform poorly on financial text. FinBERT is fine-tuned on financial news and earnings call transcripts, making it significantly more accurate for this domain.

**Airflow with failure alerts** — daily DAG with automatic retries and Slack notifications on failure so pipeline issues are caught immediately.

---

## Project Status

Work in progress. Current state:

- [x] Snowflake schema designed and provisioned
- [x] Python ingestion scripts with idempotent MERGE upserts
- [x] dbt staging and intermediate layers complete
- [x] FinBERT sentiment scoring integrated
- [x] Airflow DAG with daily schedule, retries, and Slack alerts
- [ ] Mart layer analysis and visualization
- [ ] Statistical analysis of sentiment vs earnings outcomes
- [ ] Dashboard for results

---

## What I'm Learning

Building this project taught me how production data pipelines actually work — not just moving data, but making pipelines reliable, observable, and safe to rerun. The FinBERT integration showed me how much domain matters in NLP — the difference between a general sentiment model and a finance-specific one is significant on real earnings data.

---

## Setup

```bash
# Clone the repo
git clone https://github.com/Bhoomikahp5/MarketPulse

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Add your NewsAPI key, Alpha Vantage key, and Snowflake credentials

# Run ingestion
python ingest/run_ingestion.py

# Run dbt transformations
dbt run

# Start Airflow
airflow scheduler &
airflow webserver
```

---

## Author

Bhoomika Hanbal Puttaswamy
[LinkedIn](https://www.linkedin.com/in/bhoomika-hanbal-puttaswamy) | [GitHub](https://github.com/Bhoomikahp5)
