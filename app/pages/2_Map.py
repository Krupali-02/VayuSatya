# app/pages/2_Map.py
import sqlite3
from pathlib import Path
import streamlit as st
import pandas as pd

# Path to DB
BASE_DIR = Path(__file__).resolve().parents[1].parent  # repo root
DB_PATH = BASE_DIR / "Data" / "vayusatya.db"

st.set_page_config(page_title="Report Map", layout="wide")
st.title("Report Map")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@st.cache_data
def load_reports_for_map():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            id,
            text,
            eventType,
            state,
            district,
            city,
            lat,
            lon,
            verificationStatus,
            timestamp
        FROM reports
        WHERE lat IS NOT NULL AND lon IS NOT NULL
        ORDER BY timestamp DESC
    """)
    rows = cur.fetchall()
    conn.close()

    # Convert to list of plain dicts (pickle-serializable)
    return [dict(r) for r in rows]

rows = load_reports_for_map()

if not rows:
    st.warning("No reports with location data found.")
    st.stop()

# Sidebar filters
st.sidebar.header("Filters")

event_types = sorted({r["eventType"] for r in rows})
selected_event = st.sidebar.selectbox(
    "Event Type",
    ["All"] + event_types
)

statuses = sorted({r["verificationStatus"] for r in rows})
selected_status = st.sidebar.selectbox(
    "Verification Status",
    ["All"] + statuses
)

# Filter rows
filtered = rows
if selected_event != "All":
    filtered = [r for r in filtered if r["eventType"] == selected_event]
if selected_status != "All":
    filtered = [r for r in filtered if r["verificationStatus"] == selected_status]

if not filtered:
    st.info("No reports match the selected filters.")
    st.stop()

# Prepare data for st.map
df = pd.DataFrame(filtered)

# Simple map
st.map(df[["lat", "lon"]])

# Optional: show details of selected report
st.subheader("Report Details")
selected_id = st.selectbox(
    "Select report",
    df["id"].tolist(),
    format_func=lambda x: f"#{x}"
)

selected_row = next(r for r in filtered if r["id"] == selected_id)
st.json({
    "id": selected_row["id"],
    "text": selected_row["text"],
    "eventType": selected_row["eventType"],
    "state": selected_row["state"],
    "district": selected_row["district"],
    "city": selected_row["city"],
    "lat": selected_row["lat"],
    "lon": selected_row["lon"],
    "verificationStatus": selected_row["verificationStatus"],
    "timestamp": selected_row["timestamp"],
})