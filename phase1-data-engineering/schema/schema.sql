-- ===========================================
-- Vigilyx AI - Complaint Analytics Database
-- Sprint 1.1 - Schema Design
-- ===========================================

CREATE TABLE products (
    product_code VARCHAR(20) PRIMARY KEY,
    product_name TEXT NOT NULL,
    device_code VARCHAR(20),
    launch_date DATE
);

CREATE TABLE imdrf_codes (
    imdrf_code VARCHAR(20) PRIMARY KEY,
    code_level VARCHAR(1)
        CHECK (code_level IN ('A', 'E', 'F')),
    description TEXT NOT NULL
);

CREATE TABLE complaints (
    complaint_id VARCHAR(30) PRIMARY KEY,

    product_code VARCHAR(20)
        REFERENCES products(product_code),

    received_date DATE NOT NULL,

    close_date DATE,

    event_description TEXT,

    imdrf_code VARCHAR(20)
        REFERENCES imdrf_codes(imdrf_code),

    regulatory_market VARCHAR(10),

    status VARCHAR(20)
    NOT NULL
    DEFAULT 'Open'
    CHECK (
        status IN (
            'Open',
            'Investigating',
            'Closed',
            'Reopened'
        )
    ),

    CONSTRAINT chk_dates
        CHECK (
            close_date IS NULL
            OR close_date >= received_date
        )
);

CREATE TABLE investigations (
    investigation_id VARCHAR(30) PRIMARY KEY,

    complaint_id VARCHAR(30) NOT NULL,

    investigation_start_date DATE,

    investigation_close_date DATE,

    root_cause_category TEXT,

    investigator TEXT,

    findings TEXT,

    CONSTRAINT fk_investigation_complaint
        FOREIGN KEY (complaint_id)
        REFERENCES complaints(complaint_id)
);

CREATE TABLE mdr_decisions (
    mdr_decision_id VARCHAR(30) PRIMARY KEY,

    complaint_id VARCHAR(30) NOT NULL,

    is_reportable BOOLEAN NOT NULL,

    decision_date DATE,

    decided_by TEXT,

    rationale TEXT,

    CONSTRAINT fk_mdr_complaint
        FOREIGN KEY (complaint_id)
        REFERENCES complaints(complaint_id)
);

CREATE TABLE complaint_events (
    event_id VARCHAR(30) PRIMARY KEY,

    complaint_id VARCHAR(30) NOT NULL,

    old_status VARCHAR(20),

    new_status VARCHAR(20),

    event_date DATE,

    changed_by TEXT,

    CONSTRAINT fk_event_complaint
        FOREIGN KEY (complaint_id)
        REFERENCES complaints(complaint_id)
);

CREATE INDEX idx_complaints_product_code
ON complaints(product_code);

CREATE INDEX idx_complaints_imdrf_code
ON complaints(imdrf_code);

CREATE INDEX idx_complaints_received_date
ON complaints(received_date);

CREATE INDEX idx_investigations_complaint_id
ON investigations(complaint_id);

CREATE INDEX idx_mdr_decisions_complaint_id
ON mdr_decisions(complaint_id);

CREATE INDEX idx_complaint_events_complaint_id
ON complaint_events(complaint_id);