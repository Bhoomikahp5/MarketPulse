WITH earnings AS (
    SELECT * FROM {{ ref('stg_earnings') }}
),

news AS (
    SELECT * FROM {{ ref('stg_news_articles') }}
),

latest_earnings AS (
    SELECT *
    FROM earnings
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY ticker
        ORDER BY fiscal_date DESC
    ) = 1
),

news_summary AS (
    SELECT
        ticker,
        COUNT(headline)              AS total_news_articles,
        COUNT(DISTINCT source_name)  AS unique_sources,
        MIN(published_at)            AS earliest_news,
        MAX(published_at)            AS latest_news
    FROM news
    GROUP BY ticker
),

joined AS (
    SELECT
        e.ticker,
        e.fiscal_date           AS latest_earnings_date,
        e.total_revenue         AS latest_revenue,
        e.net_income            AS latest_net_income,
        n.total_news_articles,
        n.unique_sources,
        n.earliest_news,
        n.latest_news
    FROM latest_earnings e
    LEFT JOIN news_summary n
        ON e.ticker = n.ticker
)

SELECT * FROM joined
ORDER BY total_news_articles DESC