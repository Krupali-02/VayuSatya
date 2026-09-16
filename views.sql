PRAGMA table_info(reports);
-- VayuSatya SQLite views


-- Remove old views before recreating them
DROP VIEW IF EXISTS v_reports_by_day;
DROP VIEW IF EXISTS v_reports_by_event;
DROP VIEW IF EXISTS v_reports_by_district;
DROP VIEW IF EXISTS v_verification_summary;
DROP VIEW IF EXISTS v_credibility_by_district;
DROP VIEW IF EXISTS v_credibility_by_event;
DROP VIEW IF EXISTS v_summary_by_event_type;
DROP VIEW IF EXISTS v_high_risk_reports;


-- 1. Reports by day
CREATE VIEW v_reports_by_day AS
SELECT
    DATE("timestamp") AS report_date,
    COUNT(*) AS total_reports
FROM reports
GROUP BY DATE("timestamp");


-- 2. Reports by event type
CREATE VIEW v_reports_by_event AS
SELECT
    eventType,
    COUNT(*) AS total_reports
FROM reports
GROUP BY eventType;


-- 3. Reports by district
CREATE VIEW v_reports_by_district AS
SELECT
    state,
    district,
    COUNT(*) AS total_reports
FROM reports
GROUP BY state, district;


-- 4. Verification summary
CREATE VIEW v_verification_summary AS
SELECT
    verificationStatus,
    COUNT(*) AS total_reports
FROM reports
GROUP BY verificationStatus;


-- 5. Average credibility by district
CREATE VIEW v_credibility_by_district AS
SELECT
    state,
    district,
    COUNT(*) AS report_count,
    ROUND(AVG(ml_credibility_score), 4) AS average_credibility
FROM reports
GROUP BY state, district;


-- 6. Average credibility by event type
CREATE VIEW v_credibility_by_event AS
SELECT
    eventType AS event_type,
    COUNT(*) AS report_count,
    ROUND(AVG(ml_credibility_score), 4) AS average_credibility
FROM reports
GROUP BY eventType;


-- 7. Summary by event type
CREATE VIEW v_summary_by_event_type AS
SELECT
    eventType,
    COUNT(*) AS report_count,
    AVG(ml_credibility_score) AS avg_ml_score,
    AVG(confidence) AS avg_confidence,
    SUM(
        CASE
            WHEN verificationStatus = 'Verified' THEN 1
            ELSE 0
        END
    ) * 1.0 / COUNT(*) AS verified_ratio
FROM reports
GROUP BY eventType;


-- 8. High-risk reports
CREATE VIEW v_high_risk_reports AS
SELECT
    state,
    district,
    eventType,
    COUNT(*) AS report_count,
    AVG(ml_credibility_score) AS avg_ml_score,
    SUM(
        CASE
            WHEN verificationStatus = 'Misinformation' THEN 1
            ELSE 0
        END
    ) * 1.0 / COUNT(*) AS misinformation_ratio
FROM reports
GROUP BY state, district, eventType;


-- Check all views
SELECT name, type
FROM sqlite_master
WHERE type = 'view'
ORDER BY name;


-- Test reports by day
SELECT *
FROM v_reports_by_day
ORDER BY report_date;


-- Test reports by event
SELECT *
FROM v_reports_by_event
ORDER BY total_reports DESC;


-- Test reports by district
SELECT *
FROM v_reports_by_district
ORDER BY total_reports DESC;


-- Test verification summary
SELECT *
FROM v_verification_summary
ORDER BY total_reports DESC;


-- Test credibility by district
SELECT *
FROM v_credibility_by_district
ORDER BY average_credibility ASC;


-- Test credibility by event
SELECT *
FROM v_credibility_by_event
ORDER BY average_credibility ASC;


-- Test summary by event type
SELECT *
FROM v_summary_by_event_type
ORDER BY report_count DESC;


-- Test high-risk reports
SELECT *
FROM v_high_risk_reports
ORDER BY misinformation_ratio DESC,
         avg_ml_score ASC;
		 SELECT name, type
FROM sqlite_master
WHERE type = 'view'
ORDER BY name;
