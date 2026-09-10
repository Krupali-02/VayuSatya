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

    # One shared timestamp range for ALL reports (for noise portion)
    GLOBAL_START = datetime(2026, 8, 5, 0, 0, 0)
    GLOBAL_END   = datetime(2026, 9, 8, 23, 59, 59)

    all_districts = list(CITIES_BY_DISTRICT.keys())
    all_event_types = EVENT_TYPES  # from constants

    # -------------------------
    # 1. Guaranteed-match portion: timestamps drawn FROM ground-truth windows
    # -------------------------
    # These will naturally become Verified in most cases.
    num_guaranteed_match = int(NUM_REPORTS * 0.35)  # ~35% Verified target

    for _ in range(num_guaranteed_match):
        gt_entry = random.choice(ground_truth)

        state = gt_entry["state"]
        district = gt_entry["district"]
        event_type = gt_entry["eventType"]

        # Timestamp drawn FROM this ground-truth entry's window
        ts = random_timestamp_between(gt_entry["startTime"], gt_entry["endTime"])

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
            "timestamp": ts,
        }

        v = verify_report(report)
        report["verificationStatus"] = v["verificationStatus"]
        report["verificationReason"] = v["verificationReason"]
        report["confidence"] = v["confidence"]

        reports.append(report)
        report_id += 1

    # -------------------------
    # 2. Noise portion: timestamps drawn uniformly across full campaign span
    # -------------------------
    num_noise = NUM_REPORTS - num_guaranteed_match

    for _ in range(num_noise):
        # Random event type and district, not tied to any specific ground-truth entry
        event_type = random.choice(all_event_types)
        district = random.choice(all_districts)

        # Timestamp from the GLOBAL range (most will NOT match any ground truth)
        ts = random_timestamp_between(
            GLOBAL_START.strftime("%Y-%m-%dT%H:%M:%S"),
            GLOBAL_END.strftime("%Y-%m-%dT%H:%M:%S")
        )

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
            "timestamp": ts,
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