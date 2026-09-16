# app/pages/3_Admin.py
import sqlite3
from pathlib import Path
import streamlit as st
import pandas as pd

# Path to DB
BASE_DIR = Path(__file__).resolve().parents[1].parent  # repo root
DB_PATH = BASE_DIR / "Data" / "vayusatya.db"

st.set_page_config(page_title="Admin", layout="wide")
st.title("Admin / Moderation")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@st.cache_data
def load_reports_for_admin():
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
            verificationReason,
            confidence,
            ml_credibility_score,
            reviewed,
            timestamp
        FROM reports
        ORDER BY timestamp DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

rows = load_reports_for_admin()

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

reviewed_options = ["All", "Reviewed", "Not Reviewed"]
selected_reviewed = st.sidebar.selectbox(
    "Review Status",
    reviewed_options
)

# Filter rows
filtered = rows
if selected_event != "All":
    filtered = [r for r in filtered if r["eventType"] == selected_event]
if selected_status != "All":
    filtered = [r for r in filtered if r["verificationStatus"] == selected_status]
if selected_reviewed == "Reviewed":
    filtered = [r for r in filtered if r["reviewed"] == 1]
elif selected_reviewed == "Not Reviewed":
    filtered = [r for r in filtered if (r["reviewed"] == 0 or r["reviewed"] is None)]

if not filtered:
    st.info("No reports match the selected filters.")
    st.stop()

# Show as table
df = pd.DataFrame(filtered)

# Show key columns
display_cols = [
    "id", "eventType", "state", "district", "verificationStatus",
    "confidence", "ml_credibility_score", "reviewed", "timestamp"
]
st.dataframe(df[display_cols], use_container_width=True)

# Mark as reviewed
st.subheader("Mark report as reviewed")

report_ids = df["id"].tolist()
selected_id = st.selectbox("Select report ID", report_ids)

if st.button("Mark as reviewed"):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE reports SET reviewed = 1 WHERE id = ?", (selected_id,))
    conn.commit()
    conn.close()
    st.success(f"Report #{selected_id} marked as reviewed.")
    st.cache_data.clear()
    st.rerun()