WITH source AS (
    SELECT * FROM {{ source('raw', 'earnings') }}
),

cleaned AS (
    SELECT
        ticker,
        fiscal_date::DATE                           AS fiscal_date,
        NULLIF(total_revenue, 'None')::BIGINT       AS total_revenue,
        NULLIF(net_income, 'None')::BIGINT          AS net_income,
        NULLIF(gross_profit, 'None')::BIGINT        AS gross_profit,
        loaded_at
    FROM source
)

SELECT * FROM cleaned