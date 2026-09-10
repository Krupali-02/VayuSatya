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
}

# Approximate lat/lon for demo (you can refine later)
LAT_LON_BY_DISTRICT = {
    "Ahmedabad": (23.0225, 72.5714),
    "Central Delhi": (28.6139, 77.2090),
    "Kolkata": (22.5726, 88.3639),
}

SOURCES = ["Twitter", "WhatsApp", "Facebook", "Instagram", "News Portal"]
STATES_BY_DISTRICT = {
    "Ahmedabad": "Gujarat",
    "Central Delhi": "Delhi",
    "Kolkata": "West Bengal",
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
    # Return as ISO string without timezone info
    return ts.strftime("%Y-%m-%dT%H:%M:%S")


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

    for i in range(NUM_REPORTS):
        # Randomly pick a ground-truth entry to base this report on
        gt_entry = random.choice(ground_truth)

        state = gt_entry["state"]
        district = gt_entry["district"]
        event_type = gt_entry["eventType"]

        # Generate timestamp within (or near) the event window
        ts_str = random_timestamp_between(gt_entry["startTime"], gt_entry["endTime"])

        city = random.choice(CITIES_BY_DISTRICT.get(district, [district]))
        lat, lon = LAT_LON_BY_DISTRICT.get(district, (20.0, 80.0))

        text = generate_text(event_type, district)
        source = random.choice(SOURCES)
        media_url = f"https://example.com/media/{i}.jpg"

        report = {
            "id": i + 1,
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

        # Run verification logic
        v = verify_report(report)
        report["verificationStatus"] = v["verificationStatus"]
        report["verificationReason"] = v["verificationReason"]
        report["confidence"] = v["confidence"]

        reports.append(report)

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