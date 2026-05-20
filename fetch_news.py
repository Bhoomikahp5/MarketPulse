import requests
import snowflake.connector
import os
import time
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

NEWS_KEY = os.getenv("NEWS_API_KEY")
SF_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SF_USER = os.getenv("SNOWFLAKE_USER")
SF_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")

COMPANIES = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Google",
    "AMZN": "Amazon",
    "META": "Meta",
    "TSLA": "Tesla",
    "JPM": "JPMorgan",
    "GS": "Goldman Sachs",
    "NFLX": "Netflix",
    "NVDA": "Nvidia"
}

def fetch_news(company_name):
    print(f"Fetching news for {company_name}...")
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": f"{company_name} earnings revenue",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 10,
        "apiKey": NEWS_KEY
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def create_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS RAW.NEWS_ARTICLES (
            ticker          VARCHAR(10),
            company_name    VARCHAR(50),
            headline        VARCHAR(500),
            source_name     VARCHAR(100),
            published_at    VARCHAR(50),
            url             VARCHAR(1000),
            loaded_at       TIMESTAMP
        )
    """)
    print("Table ready.")

def load_to_snowflake(records):
    print(f"Loading {len(records)} articles to Snowflake...")
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
            INSERT INTO RAW.NEWS_ARTICLES
            (ticker, company_name, headline,
             source_name, published_at, url, loaded_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            r["ticker"],
            r["company_name"],
            r["headline"],
            r["source"],
            r["published_at"],
            r["url"],
            datetime.now()
        ))
    conn.commit()
    cursor.close()
    conn.close()
    print("Done. News articles loaded successfully.")

if __name__ == "__main__":
    all_articles = []
    for ticker, company_name in COMPANIES.items():
        data = fetch_news(company_name)
        articles = data.get("articles", [])
        for article in articles:
            all_articles.append({
                "ticker": ticker,
                "company_name": company_name,
                "headline": article.get("title", "")[:500],
                "source": article.get("source", {}).get("name", "")[:100],
                "published_at": article.get("publishedAt", ""),
                "url": article.get("url", "")[:1000]
            })
        time.sleep(1)
    print(f"Total articles fetched: {len(all_articles)}")
    load_to_snowflake(all_articles)