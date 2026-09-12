USE vayusaty;

DROP VIEW IF EXISTS v_reports_by_day;
DROP VIEW IF EXISTS v_reports_by_event;
DROP VIEW IF EXISTS v_reports_by_district;
DROP VIEW IF EXISTS v_verification_summary;

CREATE VIEW v_reports_by_day AS
SELECT
    DATE(`timestamp`) AS report_date,
    COUNT(*) AS total_reports
FROM reports
GROUP BY DATE(`timestamp`);

CREATE VIEW v_reports_by_event AS
SELECT
    eventType,
    COUNT(*) AS total_reports
FROM reports
GROUP BY eventType;

CREATE VIEW v_reports_by_district AS

SELECT
    state,
    district,
    COUNT(*) AS total_reports
FROM reports
GROUP BY state, district;

CREATE VIEW v_verification_summary AS
SELECT
    verificationStatus,
    COUNT(*) AS total_reports
FROM reports
GROUP BY verificationStatus;


SELECT * FROM v_reports_by_day;
SELECT * FROM v_reports_by_event;
SELECT * FROM v_reports_by_district;
SELECT * FROM v_verification_summary;

CREATE OR REPLACE VIEW v_credibility_by_district AS
SELECT
    state,
    district,
    COUNT(*) AS report_count,
    ROUND(AVG(ml_credibility_score), 4) AS average_credibility
FROM reports
GROUP BY state, district
ORDER BY average_credibility ASC;

CREATE OR REPLACE VIEW v_credibility_by_event AS
SELECT
    eventType AS event_type,
    COUNT(*) AS report_count,
    ROUND(AVG(ml_credibility_score), 4) AS average_credibility
FROM reports
GROUP BY eventType
ORDER BY average_credibility ASC;