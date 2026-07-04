/*
============================================================
Sprint 1.3.3 - MDR Decision Audit Trail
Purpose:
Reconstruct the complete audit trail for a complaint:
Complaint -> Investigation -> MDR Decision

Author : Hema Prakash
============================================================
*/

WITH complaint_chain AS (

    SELECT

        complaint_id,
        product_code,
        received_date,
        close_date,
        status

    FROM complaints

    WHERE complaint_id = 'CMP-2021-00175'

),

investigation_chain AS (

    SELECT

        complaint_id,
        investigation_id,
        investigation_start_date,
        investigation_close_date,
        investigator,
        root_cause_category,
        findings

    FROM investigations

    WHERE complaint_id = 'CMP-2021-00175'

    ORDER BY investigation_start_date

),

decision_chain AS (

    SELECT

        complaint_id,
        mdr_decision_id,
        is_reportable,
        decision_date,
        decided_by,
        rationale

    FROM mdr_decisions

    WHERE complaint_id = 'CMP-2021-00175'

    ORDER BY decision_date

)

SELECT

    cc.complaint_id,
    cc.product_code,
    cc.received_date,
    cc.close_date,
    cc.status,

    ic.investigation_id,
    ic.investigation_start_date,
    ic.investigation_close_date,
    ic.investigator,
    ic.root_cause_category,
    ic.findings,

    dc.mdr_decision_id,
    dc.is_reportable,
    dc.decision_date,
    dc.decided_by,
    dc.rationale

FROM complaint_chain cc

LEFT JOIN investigation_chain ic

ON cc.complaint_id = ic.complaint_id

LEFT JOIN decision_chain dc

ON cc.complaint_id = dc.complaint_id

ORDER BY

    dc.decision_date;