# Complaint Analytics Database - Design Rationale

## 1. Complaints Table Grain

The grain of the `complaints` table is **one row represents one unique complaint**.

I chose this grain because a complaint is the core business entity in the complaint management process. A complaint can have multiple investigations, MDR decisions, and status changes during its lifecycle. Storing only one row per complaint avoids duplicate data, keeps the schema normalized, and makes reporting easier.

---

## 2. Reopened Complaint Handling

I created a separate `complaint_events` table instead of only updating the `status` column in the `complaints` table.

If only the current status is stored, previous status changes such as **Open → Investigating → Closed → Reopened** would be lost.

The `complaint_events` table preserves the complete history of status transitions, provides an audit trail for regulatory reviews, and supports future reporting on complaint lifecycle and reopening trends.

---

## 3. Scalability Considerations (10× Growth)

If complaint volume increases significantly, the current normalized schema will still work, but some improvements would be needed.

I would add additional indexes on frequently queried columns such as `received_date`, `status`, and `product_code` to improve query performance.

Since `event_description` stores free-text complaint narratives, I would enable PostgreSQL Full-Text Search to support efficient keyword searching.

The `complaint_events` table will grow faster than the `complaints` table because a single complaint can generate multiple status events. For larger datasets, I would partition large tables by date and archive historical records to maintain query performance.

If the system grows further, I would introduce internal surrogate keys (`BIGINT IDENTITY`) for joins while keeping business identifiers such as `CMP-000001` for reporting, APIs, and audit purposes.