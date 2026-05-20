import requests
import time
import snowflake.connector
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

ALPHA_KEY = os.getenv("ALPHA_VANTAGE_KEY")
SF_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SF_USER = os.getenv("SNOWFLAKE_USER")
SF_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")

TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "META",
           "TSLA", "JPM", "GS", "NFLX", "NVDA"]

def fetch_income_statement(ticker):
    print(f"Fetching data for {ticker}...")
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "INCOME_STATEMENT",
        "symbol": ticker,
        "apikey": ALPHA_KEY
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def create_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS RAW.EARNINGS (
            ticker          VARCHAR(10),
            fiscal_date     VARCHAR(20),
            total_revenue   VARCHAR(30),
            net_income      VARCHAR(30),
            gross_profit    VARCHAR(30),
            loaded_at       TIMESTAMP
        )
    """)
    print("Table ready.")

def load_to_snowflake(records):
    print(f"Loading {len(records)} records to Snowflake...")
    conn = snowflake.connector.connect(
        account=SF_ACCOUNT,
        user=SF_USER,
        password=SF_PASSWORD,
        database="FINANCIAL_INTELLIGENCE",
        schema="RAW",
        warehouse="COMPUTE_WH"
    )
    cursor = conn.cursor()
    create_table(cursor)
    for r in records:
        cursor.execute("""
            INSERT INTO RAW.EARNINGS
            (ticker, fiscal_date, total_revenue,
             net_income, gross_profit, loaded_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            r["ticker"],
            r["fiscal_date"],
            r.get("totalRevenue", "None"),
            r.get("netIncome", "None"),
            r.get("grossProfit", "None"),
            datetime.utcnow()
        ))
    conn.commit()
    cursor.close()
    conn.close()
    print("Done. Data loaded successfully.")

if __name__ == "__main__":
    all_records = []
    for ticker in TICKERS:
        data = fetch_income_statement(ticker)
        time.sleep(12)
        reports = data.get("annualReports", [])
        for report in reports:
            report["ticker"] = ticker
            report["fiscal_date"] = report.get("fiscalDateEnding", "")
            all_records.append(report)
    print(f"Total records fetched: {len(all_records)}")
    load_to_snowflake(all_records)