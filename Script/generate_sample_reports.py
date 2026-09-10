# generate_sample_reports.py
# Purpose: Generate sample_reports.csv using:
# - constants.EVENT_TYPES
# - data/ground_truth.json
# - verification.verify_report()

import json
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# Adjust imports based on your actual folder structure
from constants import EVENT_TYPES
from verification import verify_report


# ----------------------
# Config
# ----------------------
NUM_REPORTS = 200  # total rows to generate

# Simple list of cities per district for demo (extend as needed)
CITIES_BY_DISTRICT = {
    "Ahmedabad": ["Ahmedabad", "Gandhinagar"],
    "Central Delhi": ["Central Delhi", "New Delhi"],
    "Kolkata": ["Kolkata", "Howrah"],
    "Mumbai": ["Mumbai", "Thane"],
    "Amritsar": ["Amritsar"],
    "Jaipur": ["Jaipur"],
    "Chennai": ["Chennai"],
}

# Approximate lat/lon for demo (you can refine later)
LAT_LON_BY_DISTRICT = {
    "Ahmedabad": (23.0225, 72.5714),
    "Central Delhi": (28.6139, 77.2090),
    "Kolkata": (22.5726, 88.3639),
    "Mumbai": (19.0760, 72.8777),
    "Amritsar": (31.6340, 74.8723),
    "Jaipur": (26.9124, 75.7873),
    "Chennai": (13.0827, 80.2707),
}

SOURCES = ["Twitter", "WhatsApp", "Facebook", "Instagram", "News Portal"]

STATES_BY_DISTRICT = {
    "Ahmedabad": "Gujarat",
    "Central Delhi": "Delhi",
    "Kolkata": "West Bengal",
    "Mumbai": "Maharashtra",
    "Amritsar": "Punjab",
    "Jaipur": "Rajasthan",
    "Chennai": "Tamil Nadu",
}


# ----------------------
# Helpers
# ----------------------
def load_ground_truth():
    with open("../data/ground_truth.json", encoding="utf-8") as f:
        return json.load(f)


def random_timestamp_between(start_str: str, end_str: str) -> str:
    start = datetime.fromisoformat(start_str)
    end = datetime.fromisoformat(end_str)
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    ts = start + timedelta(seconds=random_seconds)
    return ts.strftime("%Y-%m-%dT%H:%M:%S")


def jitter_lat_lon(lat: float, lon: float, max_offset_deg: float = 0.02) -> tuple:
    """
    Add small random jitter to lat/lon so reports don't stack exactly.
    max_offset_deg ~ 0.02 degrees ≈ 2 km.
    """
    lat_jitter = random.uniform(-max_offset_deg, max_offset_deg)
    lon_jitter = random.uniform(-max_offset_deg, max_offset_deg)
    return round(lat + lat_jitter, 4), round(lon + lon_jitter, 4)


def generate_text(event_type: str, district: str) -> str:
    templates = [
        f"Severe {event_type} reported in {district}.",
        f"Heavy {event_type} happening right now in {district}.",
        f"Multiple people affected by {event_type} in {district}.",
        f"Urgent: {event_type} situation worsening in {district}.",
        f"Local authorities responding to {event_type} in {district}.",
    ]
    return random.choice(templates)


# ----------------------
# Main generation logic
# ----------------------
def generate_reports():
    ground_truth = load_ground_truth()

    reports = []
    report_id = 1

    # -------------------------
    # 1. Generate Verified reports (match ground truth)
    # -------------------------
    num_verified = int(NUM_REPORTS * 0.6)  # ~60% verified
    for _ in range(num_verified):
        gt_entry = random.choice(ground_truth)

        state = gt_entry["state"]
        district = gt_entry["district"]
        event_type = gt_entry["eventType"]

        ts_str = random_timestamp_between(gt_entry["startTime"], gt_entry["endTime"])

        city = random.choice(CITIES_BY_DISTRICT.get(district, [district]))
        lat, lon = jitter_lat_lon(*LAT_LON_BY_DISTRICT.get(district, (20.0, 80.0)))

        text = generate_text(event_type, district)
        source = random.choice(SOURCES)
        media_url = f"https://example.com/media/{report_id}.jpg"

        report = {
            "id": report_id,
            "text": text,
            "eventType": event_type,
            "state": state,
            "district": district,
            "city": city,
            "lat": lat,
            "lon": lon,
            "mediaUrl": media_url,
            "source": source,
            "timestamp": ts_str,
        }

        v = verify_report(report)
        report["verificationStatus"] = v["verificationStatus"]
        report["verificationReason"] = v["verificationReason"]
        report["confidence"] = v["confidence"]

        reports.append(report)
        report_id += 1

    # -------------------------
    # 2. Generate Suspicious reports (extreme events with NO match)
    # -------------------------
    extreme_events = ["Flood", "Thunderstorm", "Heatwave", "Dust Storm"]
    num_suspicious = int(NUM_REPORTS * 0.25)  # ~25% suspicious

    for _ in range(num_suspicious):
        event_type = random.choice(extreme_events)

        # Pick a random district from our list
        all_districts = list(CITIES_BY_DISTRICT.keys())
        district = random.choice(all_districts)

        # Time far outside any ground-truth window
        base_date = datetime(2026, 9, 1, 12, 0, 0)
        offset_days = random.randint(-10, -4)  # well before any ground truth
        ts = base_date + timedelta(days=offset_days, hours=random.randint(0, 23))
        ts_str = ts.strftime("%Y-%m-%dT%H:%M:%S")

        state = STATES_BY_DISTRICT.get(district, "Unknown")
        city = random.choice(CITIES_BY_DISTRICT.get(district, [district]))
        lat, lon = jitter_lat_lon(*LAT_LON_BY_DISTRICT.get(district, (20.0, 80.0)))

        text = generate_text(event_type, district)
        source = random.choice(SOURCES)
        media_url = f"https://example.com/media/{report_id}.jpg"

        report = {
            "id": report_id,
            "text": text,
            "eventType": event_type,
            "state": state,
            "district": district,
            "city": city,
            "lat": lat,
            "lon": lon,
            "mediaUrl": media_url,
            "source": source,
            "timestamp": ts_str,
        }

        v = verify_report(report)
        report["verificationStatus"] = v["verificationStatus"]
        report["verificationReason"] = v["verificationReason"]
        report["confidence"] = v["confidence"]

        reports.append(report)
        report_id += 1

    # -------------------------
    # 3. Generate Pending reports (ordinary events with NO match)
    # -------------------------
    ordinary_events = ["Rainfall", "Fog", "Strong Winds"]
    num_pending = NUM_REPORTS - num_verified - num_suspicious

    for _ in range(num_pending):
        event_type = random.choice(ordinary_events)

        all_districts = list(CITIES_BY_DISTRICT.keys())
        district = random.choice(all_districts)

        # Time far outside any ground-truth window
        base_date = datetime(2026, 8, 20, 12, 0, 0)
        offset_days = random.randint(-15, -5)
        ts = base_date + timedelta(days=offset_days, hours=random.randint(0, 23))
        ts_str = ts.strftime("%Y-%m-%dT%H:%M:%S")

        state = STATES_BY_DISTRICT.get(district, "Unknown")
        city = random.choice(CITIES_BY_DISTRICT.get(district, [district]))
        lat, lon = jitter_lat_lon(*LAT_LON_BY_DISTRICT.get(district, (20.0, 80.0)))

        text = generate_text(event_type, district)
        source = random.choice(SOURCES)
        media_url = f"https://example.com/media/{report_id}.jpg"

        report = {
            "id": report_id,
            "text": text,
            "eventType": event_type,
            "state": state,
            "district": district,
            "city": city,
            "lat": lat,
            "lon": lon,
            "mediaUrl": media_url,
            "source": source,
            "timestamp": ts_str,
        }

        v = verify_report(report)
        report["verificationStatus"] = v["verificationStatus"]
        report["verificationReason"] = v["verificationReason"]
        report["confidence"] = v["confidence"]

        reports.append(report)
        report_id += 1

    return reports


def save_to_csv(reports, output_path: str):
    if not reports:
        return

    fieldnames = list(reports[0].keys())
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(reports)


if __name__ == "__main__":
    reports = generate_reports()
    output_csv = "../data/sample_reports.csv"
    save_to_csv(reports, output_csv)
    print(f"Generated {len(reports)} reports → {output_csv}")