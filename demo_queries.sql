USE vayusaty;

SELECT
    city,
    district,
    `timestamp`,
    text,
    verificationReason,
    confidence
FROM reports
WHERE state = 'Gujarat'
  AND eventType = 'Flood'
  AND verificationStatus = 'Suspicious'
ORDER BY `timestamp` DESC;

SELECT
    state,
    district,
    COUNT(*) AS heatwave_count
FROM reports
WHERE eventType = 'Heatwave'
GROUP BY state, district
ORDER BY heatwave_count DESC
LIMIT 5;

SELECT
    verificationStatus,
    COUNT(*) AS report_count
FROM reports
GROUP BY verificationStatus
ORDER BY report_count DESC;

SELECT
    state,
    COUNT(*) AS report_count
FROM reports
GROUP BY state
ORDER BY report_count DESC;

SELECT
    eventType,
    COUNT(*) AS report_count
FROM reports
GROUP BY eventType
ORDER BY report_count DESC;