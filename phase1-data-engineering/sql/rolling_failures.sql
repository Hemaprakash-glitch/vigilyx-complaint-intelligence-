/*
============================================================
Sprint 1.3.2 - Rolling 30-Day Device Failure Count
Purpose:
Identify products with repeated complaints within a rolling
30-day window using SQL Window Functions.
============================================================
*/

SELECT

    complaint_id,

    product_code,

    received_date,

    COUNT(*) OVER (

        PARTITION BY product_code

        ORDER BY received_date

        RANGE BETWEEN INTERVAL '30 days' PRECEDING
        AND CURRENT ROW

    ) AS rolling_30day_count

FROM complaints

ORDER BY

    product_code,

    received_date;