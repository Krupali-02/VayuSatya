USE vayusaty;

-- 1. Check total number of reports
SELECT
    COUNT(*) AS total_reports
FROM reports;


-- 2. Check report IDs that are repeated
SELECT
    id,
    COUNT(*) AS duplicate_count
FROM reports
GROUP BY id
HAVING COUNT(*) > 1;


-- 3. Check empty important values
SELECT
    SUM(CASE WHEN `timestamp` IS NULL THEN 1 ELSE 0 END) AS empty_timestamp,
    SUM(CASE WHEN eventType IS NULL OR eventType = '' THEN 1 ELSE 0 END) AS empty_event_type,
    SUM(CASE WHEN state IS NULL OR state = '' THEN 1 ELSE 0 END) AS empty_state,
    SUM(CASE WHEN district IS NULL OR district = '' THEN 1 ELSE 0 END) AS empty_district,
    SUM(CASE WHEN verificationStatus IS NULL OR verificationStatus = '' THEN 1 ELSE 0 END) AS empty_status
FROM reports;


-- 4. Check event type totals
SELECT
    eventType,
    COUNT(*) AS report_count
FROM reports
GROUP BY eventType
ORDER BY eventType;


-- 5. Check verification status totals
SELECT
    verificationStatus,
    COUNT(*) AS report_count
FROM reports
GROUP BY verificationStatus
ORDER BY verificationStatus;


-- 6. Check the four views
SELECT * FROM v_reports_by_day;

SELECT * FROM v_reports_by_event;

SELECT * FROM v_reports_by_district;

SELECT * FROM v_verification_summary;


-- 7. Check that event totals equal 200
SELECT
    SUM(total_reports) AS total_from_event_view
FROM v_reports_by_event;


-- 8. Check that verification totals equal 200
SELECT
    SUM(total_reports) AS total_from_status_view
FROM v_verification_summary;
