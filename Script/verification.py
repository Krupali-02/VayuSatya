# verification.py
# Purpose: Implement the core verification logic that labels each report
# as Verified / Suspicious / Pending by comparing it against official
# ground-truth warnings (IMD-like). Uses normalized string matching and
# naive timestamps to avoid common bugs.

import json
from datetime import datetime, timedelta

# Load ground truth from data/ground_truth.json
with open("../data/ground_truth.json") as f:
    GROUND_TRUTH = json.load(f)

# verification.py

def parse_ts(ts_str: str) -> datetime:
    """
    Parse timestamp string to naive datetime.
    Strips 'Z' and timezone offsets to avoid naive/aware comparison errors.
    """
    if ts_str is None:
        return None
    if not isinstance(ts_str, str):
        # Fallback: convert to string if somehow it's not
        ts_str = str(ts_str)

    ts_str = ts_str.replace("Z", "").split("+")[0]
    # Ensure we only take the first 19 chars (YYYY-MM-DDTHH:MM:SS)
    ts_str = ts_str[:19]
    return datetime.fromisoformat(ts_str)

def is_within_window(ts: datetime, start: str, end: str, hours: int = 3) -> bool:
    if ts is None:
        return False
    start_dt = parse_ts(start)
    end_dt = parse_ts(end)
    if start_dt is None or end_dt is None:
        return False
    buffer = timedelta(hours=hours)
    return (start_dt - buffer) <= ts <= (end_dt + buffer)

def verify_report(report: dict) -> dict:
    """
    Verify a single report against ground truth.

    Returns:
    {
        "verificationStatus": "Verified" | "Suspicious" | "Pending",
        "verificationReason": "...",
        "confidence": 0.0–1.0
    }
    """
    # Normalize strings for robust matching
    district = (report.get("district") or "").strip().lower()
    event_type = (report.get("eventType") or "").strip().lower()
    ts_str = report.get("timestamp")
    ts = parse_ts(ts_str) if ts_str else None

    # Find matching ground-truth entries
    matches = [
        g for g in GROUND_TRUTH
        if g["district"].strip().lower() == district
        and g["eventType"].strip().lower() == event_type
        and is_within_window(ts, g["startTime"], g["endTime"], hours=3)
    ]

    if matches:
        return {
            "verificationStatus": "Verified",
            "verificationReason": f"Matches {len(matches)} official warning(s) for {event_type} in {district}.",
            "confidence": 0.9
        }

    # Extreme events with no match → Suspicious
    extreme_events = {"flood", "thunderstorm", "heatwave", "dust storm"}
    if event_type in extreme_events:
        return {
            "verificationStatus": "Suspicious",
            "verificationReason": f"No official warning found for {event_type} in {district}; extreme event claim.",
            "confidence": 0.6
        }

    # Ordinary events with no match → Pending (not Fake by default)
    return {
        "verificationStatus": "Pending",
        "verificationReason": f"No official warning found for {event_type} in {district}; ordinary event, unverified.",
        "confidence": 0.5
    }