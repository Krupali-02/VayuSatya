# constants.py
# Purpose: Define the official list of event types so that
# - ground truth JSON
# - generated reports
# - verification logic
# - MERN/Streamlit dropdowns
# all use the exact same strings. This avoids mismatches like
# "Flood" vs "flooding" vs "flood".

EVENT_TYPES = [
    "Rainfall",
    "Thunderstorm",
    "Flood",
    "Heatwave",
    "Fog",
    "Dust Storm",
    "Strong Winds"
]

# Lowercase versions are used for case-insensitive matching
EVENT_TYPES_LOWER = [e.lower() for e in EVENT_TYPES]