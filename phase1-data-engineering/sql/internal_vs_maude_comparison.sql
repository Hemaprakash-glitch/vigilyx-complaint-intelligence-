/*
============================================================
Sprint 1.4.3 - Internal vs MAUDE Comparison
Purpose:
Compare internal complaint volume with external FDA MAUDE
events for a given product code.

The normalized metric represents internal complaints per
1000 MAUDE events and is intended for trend comparison,
not as an absolute complaint rate.

Author : Hema Prakash
============================================================
*/

WITH internal_counts AS (

    SELECT

        product_code,

        COUNT(*) AS internal_count

    FROM complaints

    WHERE product_code = 'OZO'

    GROUP BY product_code

),

maude_counts AS (

    SELECT

        product_code,

        COUNT(*) AS maude_count

    FROM maude_external_events

    WHERE product_code = 'OZO'

    GROUP BY product_code

)

SELECT

    COALESCE(i.product_code, m.product_code)
        AS product_code,

    COALESCE(i.internal_count, 0)
        AS internal_count,

    COALESCE(m.maude_count, 0)
        AS maude_count,

    ROUND(

        (
            COALESCE(i.internal_count, 0)::NUMERIC
            /
            NULLIF(COALESCE(m.maude_count, 0), 0)
        ) * 1000,

        2

    ) AS internal_per_1000_maude_events

FROM internal_counts i

FULL OUTER JOIN maude_counts m

ON i.product_code = m.product_code;