/*
============================================================
Sprint 1.3.2 - Reopen Detection
Purpose:
Identify complaints that were reopened by analysing
complaint status history using ROW_NUMBER().
============================================================
*/

SELECT

    complaint_id,

    old_status,

    new_status,

    event_date,

    ROW_NUMBER() OVER (

        PARTITION BY complaint_id

        ORDER BY event_date

    ) AS event_sequence

FROM complaint_events

WHERE new_status = 'Reopened'

ORDER BY

    complaint_id,

    event_date;