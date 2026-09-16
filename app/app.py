# app/app.py
from datetime import datetime
from pathlib import Path
import sqlite3

import streamlit as st

# Import shared constants and helpers
import sys
SCRIPT_PATH = Path(__file__).parent.parent / "Script"
sys.path.insert(0, str(SCRIPT_PATH))

from constants import EVENT_TYPES
from verification import verify_report

# ----------------------
# Shared location data: state -> district -> list of (city, lat, lon)
# ----------------------
LOCATION_DATA = {
    "Gujarat": {
        "Ahmedabad": [
            ("Ahmedabad", 23.0225, 72.5714),
            ("Gandhinagar", 23.2150, 72.6369),
        ],
    },
    "Delhi": {
        "Central Delhi": [
            ("Central Delhi", 28.6139, 77.2090),
            ("New Delhi", 28.6139, 77.2090),
        ],
    },
    "West Bengal": {
        "Kolkata": [
            ("Kolkata", 22.5726, 88.3639),
            ("Howrah", 22.5958, 88.2636),
        ],
    },
    "Maharashtra": {
        "Mumbai": [
            ("Mumbai", 19.0760, 72.8777),
            ("Thane", 19.2183, 72.9781),
        ],
    },
    "Punjab": {
        "Amritsar": [
            ("Amritsar", 31.6340, 74.8723),
        ],
    },
    "Rajasthan": {
        "Jaipur": [
            ("Jaipur", 26.9124, 75.7873),
        ],
    },
    "Tamil Nadu": {
        "Chennai": [
            ("Chennai", 13.0827, 80.2707),
        ],
    },
}

ALL_STATES = list(LOCATION_DATA.keys())

def get_districts_for_state(state):
    return list(LOCATION_DATA[state].keys())

def get_cities_for_district(state, district):
    # Returns list of (city_name, lat, lon)
    return LOCATION_DATA[state][district]

# ----------------------
# Paths
# ----------------------
DATA_DIR = Path(__file__).parent.parent / "Data"
DB_PATH = DATA_DIR / "vayusatya.db"

# ----------------------
# DB helpers
# ----------------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def save_report_to_db(report: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO reports (
        text, eventType, state, district, city,
        lat, lon, mediaUrl, source, timestamp,
        verificationStatus, verificationReason, confidence, ml_credibility_score
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        report["text"],
        report["eventType"],
        report["state"],
        report["district"],
        report["city"],
        report["lat"],
        report["lon"],
        report["mediaUrl"],
        report["source"],
        report["timestamp"],
        report["verificationStatus"],
        report["verificationReason"],
        report["confidence"],
        report["ml_credibility_score"],
    ))
    conn.commit()
    conn.close()

# ----------------------
# Page config
# ----------------------
st.set_page_config(page_title="Citizen Report Form", layout="centered")
st.title("Citizen Disaster Report Form")

# ----------------------
# Session state for selections and lat/lon
# ----------------------
if "state" not in st.session_state:
    st.session_state.state = "Gujarat"
if "district" not in st.session_state:
    st.session_state.district = "Ahmedabad"
if "city" not in st.session_state:
    st.session_state.city = "Ahmedabad"
if "lat" not in st.session_state:
    st.session_state.lat = 23.0225
if "lon" not in st.session_state:
    st.session_state.lon = 72.5714

def update_location():
    state = st.session_state.state
    district = st.session_state.district
    cities_data = get_cities_for_district(state, district)
    # Default to first city
    city_name, lat, lon = cities_data[0]
    st.session_state.city = city_name
    st.session_state.lat = lat
    st.session_state.lon = lon

# When state changes, update district/city/lat/lon
def on_state_change():
    state = st.session_state.state
    districts = get_districts_for_state(state)
    st.session_state.district = districts[0]
    update_location()

# When district changes, update city/lat/lon
def on_district_change():
    update_location()

# When city changes, update lat/lon
def on_city_change():
    state = st.session_state.state
    district = st.session_state.district
    city_name = st.session_state.city
    cities_data = get_cities_for_district(state, district)
    for c_name, lat, lon in cities_data:
        if c_name == city_name:
            st.session_state.lat = lat
            st.session_state.lon = lon
            break

# ----------------------
# Location selectors (outside the form so on_change is allowed)
# ----------------------
state = st.selectbox(
    "State",
    ALL_STATES,
    key="state",
    on_change=on_state_change
)

districts = get_districts_for_state(state)
district = st.selectbox(
    "District",
    districts,
    key="district",
    on_change=on_district_change
)

cities_data = get_cities_for_district(state, district)
city_names = [c[0] for c in cities_data]
city = st.selectbox(
    "City/Town/Village",
    city_names,
    key="city",
    on_change=on_city_change
)

# Display auto-filled lat/lon (read-only)
st.text_input("Latitude (auto-filled)", value=f"{st.session_state.lat:.4f}", disabled=True)
st.text_input("Longitude (auto-filled)", value=f"{st.session_state.lon:.4f}", disabled=True)

# ----------------------
# Report form
# ----------------------
with st.form("report_form", clear_on_submit=True):
    text = st.text_area("Describe what you observed (2–3 sentences)", height=100)

    event_type = st.selectbox(
        "Event Type",
        EVENT_TYPES + ["Other"]
    )

    # State/district/city already selected above; just use those values

    media_url = st.text_input("Media URL (image/video link) [optional]")

    source = st.selectbox(
        "Source of information",
        ["Twitter", "WhatsApp", "Facebook", "Instagram", "News Portal", "Other"]
    )

    timestamp = st.datetime_input("Timestamp of event", value=datetime.now())

    submitted = st.form_submit_button("Submit Report")

if submitted:
    if not text:
        st.error("Please fill in the report text.")
    else:
        report = {
            "text": text,
            "eventType": event_type,
            "state": state,
            "district": district,
            "city": city,
            "lat": st.session_state.lat,
            "lon": st.session_state.lon,
            "mediaUrl": media_url or "",
            "source": source,
            "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
        }

        v = verify_report(report)
        report["verificationStatus"] = v["verificationStatus"]
        report["verificationReason"] = v["verificationReason"]
        report["confidence"] = v["confidence"]
        report["ml_credibility_score"] = v["ml_credibility_score"]

        save_report_to_db(report)

        st.success("Report submitted successfully!")
        st.write("**Verification Status:**", report["verificationStatus"])
        st.write("**Reason:**", report["verificationReason"])
        st.write("**Confidence:**", f"{report['confidence']:.2f}")
        st.write("**ML Credibility Score:**", f"{report['ml_credibility_score']:.2f}")

        from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]  # repo root, adjust if needed
DB_PATH = BASE_DIR / "Data" / "vayusatya.db"