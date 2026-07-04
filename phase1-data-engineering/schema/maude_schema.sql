/*
============================================================
Sprint 1.4.3 - MAUDE External Events Schema
Purpose:
Store external FDA MAUDE records separately from
internal complaint records.

Author : Hema Prakash
============================================================
*/

DROP TABLE IF EXISTS maude_external_events;

CREATE TABLE maude_external_events (

    maude_event_id VARCHAR(30) PRIMARY KEY,

    product_code VARCHAR(20),

    device_name TEXT,

    event_type VARCHAR(50),

    date_received DATE,

    source_search_term TEXT,

    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);