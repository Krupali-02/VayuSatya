# app/pages/1_Reports_Preview.py
import sqlite3
import pandas as pd
import streamlit as st
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "Data" / "vayusatya.db"

st.set_page_config(page_title="Reports Preview", layout="wide")
st.title("Reports Preview")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@st.cache_data(ttl=5)  # refresh at least every 5 seconds
def load_reports():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM reports", conn)
    conn.close()
    return df

df = load_reports()

st.write(f"Total reports: {len(df)}")

# Simple filters
col1, col2, col3 = st.columns(3)
with col1:
    states = sorted(df["state"].dropna().unique())
    selected_state = st.selectbox("State", ["All"] + list(states))
with col2:
    event_types = sorted(df["eventType"].dropna().unique())
    selected_event = st.selectbox("Event Type", ["All"] + list(event_types))
with col3:
    statuses = sorted(df["verificationStatus"].dropna().unique())
    selected_status = st.selectbox("Verification Status", ["All"] + list(statuses))

filtered = df.copy()
if selected_state != "All":
    filtered = filtered[filtered["state"] == selected_state]
if selected_event != "All":
    filtered = filtered[filtered["eventType"] == selected_event]
if selected_status != "All":
    filtered = filtered[filtered["verificationStatus"] == selected_status]

st.write(f"Filtered reports: {len(filtered)}")

cols_to_show = [
    "id",
    "timestamp",
    "state",
    "district",
    "eventType",
    "verificationStatus",
    "ml_credibility_score",
    "text",
]
st.dataframe(filtered[cols_to_show], use_container_width=True)