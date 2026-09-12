
CREATE DATABASE IF NOT EXISTS vayusaty;

USE vayusaty;

SELECT DATABASE();

CREATE TABLE IF NOT EXISTS reports (
    id INT NOT NULL,
    text TEXT NOT NULL,
    eventType VARCHAR(50) NOT NULL,
    state VARCHAR(50),
    district VARCHAR(100),
    city VARCHAR(100),
    lat DECIMAL(10, 6),
    lon DECIMAL(10, 6),
    mediaUrl VARCHAR(500),
    source VARCHAR(100),
    `timestamp` DATETIME NOT NULL,
    verificationStatus VARCHAR(30) NOT NULL,
    verificationReason TEXT,
    confidence DECIMAL(5, 2),
    ml_credibility_score DECIMAL(5, 4),
    PRIMARY KEY (id)
);