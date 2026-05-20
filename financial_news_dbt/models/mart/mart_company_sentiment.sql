WITH news AS (
    SELECT * FROM {{ ref('stg_news_articles') }}
),

sentiment_summary AS (
    SELECT
        ticker,
        company_name,
        DATE_TRUNC('month', published_at)   AS news_month,
        COUNT(*)                            AS total_articles,
        COUNT(DISTINCT source_name)         AS unique_sources
    FROM news
    GROUP BY ticker, company_name, DATE_TRUNC('month', published_at)
)

SELECT * FROM sentiment_summary