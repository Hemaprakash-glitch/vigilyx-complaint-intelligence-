/*
Complaint Aging Report
Open complaints grouped by SLA aging buckets
*/

WITH open_complaints AS (

    SELECT

        c.complaint_id,
        c.product_code,
        c.received_date,

        CURRENT_DATE - c.received_date
        AS complaint_age

    FROM complaints c

    LEFT JOIN mdr_decisions m

    ON c.complaint_id = m.complaint_id

    WHERE m.complaint_id IS NULL

)

SELECT

    CASE

        WHEN complaint_age <= 30 THEN '0-30 Days'

        WHEN complaint_age <= 60 THEN '31-60 Days'

        WHEN complaint_age <= 90 THEN '61-90 Days'

        ELSE '90+ Days'

    END AS aging_bucket,

    product_code,

    COUNT(*) AS complaint_count

FROM open_complaints

GROUP BY

    aging_bucket,
    product_code

ORDER BY

    aging_bucket,
    product_code;