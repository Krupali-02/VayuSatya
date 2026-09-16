# verification.py
# Purpose: Implement the core verification logic that labels each report
# as Verified / Unverified / Misinformation by comparing it against official
# ground-truth warnings. Uses normalized string matching and naive timestamps.

import json
from datetime import datetime, timedelta
from pathlib import Path

from ml_verification import load_ml_model, predict_credibility

# ----------------------
# Load ground truth and ML model once at import time
# ----------------------
SCRIPT_DIR = Path(__file__).parent
GROUND_TRUTH_PATH = SCRIPT_DIR.parent / "Data" / "ground_truth.json"

with open(GROUND_TRUTH_PATH, encoding="utf-8") as f:
    GROUND_TRUTH = json.load(f)

_ML_MODEL = load_ml_model()

# ----------------------
# Helpers
# ----------------------
def parse_ts(ts_str: str) -> datetime:
    """
    Parse timestamp string to naive datetime.
    Strips 'Z' and timezone offsets to avoid naive/aware comparison errors.
    """
    if ts_str is None:
        return None
    if not isinstance(ts_str, str):
        ts_str = str(ts_str)

    ts_str = ts_str.replace("Z", "").split("+")[0]
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


def matches_location(report, gt_entry) -> bool:
    r_district = (report.get("district") or "").strip().lower()
    g_district = (gt_entry.get("district") or "").strip().lower()

    r_state = (report.get("state") or "").strip().lower()
    g_state = (gt_entry.get("state") or "").strip().lower()

    district_match = r_district and r_district == g_district
    state_match = r_state and r_state == g_state

    r_lat = report.get("lat")
    r_lon = report.get("lon")
    g_lat = gt_entry.get("lat")
    g_lon = gt_entry.get("lon")

    lat_lon_match = False
    if all(v is not None for v in [r_lat, r_lon, g_lat, g_lon]):
        lat_match = abs(float(r_lat) - float(g_lat)) <= 0.1
        lon_match = abs(float(r_lon) - float(g_lon)) <= 0.1
        lat_lon_match = lat_match and lon_match

    return (district_match and state_match) or lat_lon_match


def matches_time(report, gt_entry) -> bool:
    ts_str = report.get("timestamp")
    if not ts_str:
        return False
    try:
        report_time = parse_ts(ts_str)
    except Exception:
        return False

    start = parse_ts(gt_entry["startTime"])
    end = parse_ts(gt_entry["endTime"])

    if start <= report_time <= end:
        return True

    buffer = timedelta(hours=3)
    if (start - buffer) <= report_time <= (end + buffer):
        return True

    return False


def matches_event_type(report, gt_entry) -> bool:
    r_event = (report.get("eventType") or "").strip().lower()
    g_event = (gt_entry.get("eventType") or "").strip().lower()
    return r_event and r_event == g_event


# ----------------------
# Main verification function
# ----------------------
def verify_report(report: dict) -> dict:
    """
    Verify a single report against ground truth.

    Returns:
    {
        "verificationStatus": "Verified" | "Unverified" | "Misinformation",
        "verificationReason": "...",
        "confidence": 0.0–1.0,
        "ml_credibility_score": 0.0–1.0
    }
    """
    district = (report.get("district") or "").strip().lower()
    event_type = (report.get("eventType") or "").strip().lower()
    ts_str = report.get("timestamp")
    ts = parse_ts(ts_str) if ts_str else None

    # 1. Filter to same event type first
    candidates = [
        g for g in GROUND_TRUTH
        if matches_event_type(report, g)
    ]

    if not candidates:
        # No ground-truth event of this type at all
        ml_score = predict_credibility(report.get("text", ""), model=_ML_MODEL)
        if ml_score < 0.4:
            return {
                "verificationStatus": "Misinformation",
                "verificationReason": "No matching ground truth event and low ML credibility score.",
                "confidence": 0.7,
                "ml_credibility_score": ml_score,
            }
        return {
            "verificationStatus": "Unverified",
            "verificationReason": "No matching ground truth event type found.",
            "confidence": 0.5,
            "ml_credibility_score": ml_score,
        }

    # 2. Check for any full match (event + location + time) across ALL candidates
    full_match_exists = any(
        matches_location(report, g) and matches_time(report, g)
        for g in candidates
    )

    ml_score = predict_credibility(report.get("text", ""), model=_ML_MODEL)

    if full_match_exists:
        return {
            "verificationStatus": "Verified",
            "verificationReason": f"Matches official warning(s) for {event_type} in {district}.",
            "confidence": 0.9,
            "ml_credibility_score": ml_score,
        }

    # 3. No full match: check for partial matches
    loc_match_exists = any(matches_location(report, g) for g in candidates)
    time_match_exists = any(matches_time(report, g) for g in candidates)

    if loc_match_exists and not time_match_exists:
        return {
            "verificationStatus": "Unverified",
            "verificationReason": f"Location matches, but timestamp outside event window for {event_type} in {district}.",
            "confidence": 0.6,
            "ml_credibility_score": ml_score,
        }

    if time_match_exists and not loc_match_exists:
        return {
            "verificationStatus": "Unverified",
            "verificationReason": f"Time matches, but location does not match event area for {event_type}.",
            "confidence": 0.5,
            "ml_credibility_score": ml_score,
        }

    # 4. No meaningful match at all
    if ml_score < 0.4:
        return {
            "verificationStatus": "Misinformation",
            "verificationReason": "No matching ground truth event and low ML credibility score.",
            "confidence": 0.7,
            "ml_credibility_score": ml_score,
        }

    return {
        "verificationStatus": "Unverified",
        "verificationReason": f"No matching ground truth event found for {event_type} in {district}.",
        "confidence": 0.5,
        "ml_credibility_score": ml_score,
    }