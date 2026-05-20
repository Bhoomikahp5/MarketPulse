WITH source AS (
    SELECT * FROM {{ source('raw', 'news_articles') }}
),

cleaned AS (
    SELECT
        ticker,
        company_name,
        headline,
        source_name,
        published_at::TIMESTAMP        AS published_at,
        url,
        loaded_at
    FROM source
    WHERE headline IS NOT NULL
      AND headline != ''
)

SELECT * FROM cleaned