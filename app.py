import streamlit as st
from streamlit_folium import st_folium
import folium
import random
import pandas as pd
from datetime import datetime, timedelta

# --- 1. MOCK TEMPORAL DATA GENERATOR (With Geofencing) ---
def get_historical_activity(lat, lon, is_sensitive):
    activities = []
    random.seed(int(lat * 1000) + int(lon * 1000)) 
    
    # If NOT in a sensitive zone, the probability of military activity drops to almost zero
    probability = 0.6 if is_sensitive else 0.05 
    
    for i in range(3):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        if random.random() < probability:
            event = random.choice([
                "New Concrete Foundation (Bunker Type)", 
                "Metallic Cluster (Possible Convoy)", 
                "Trench Extension Detected",
                "Earth Moving Equipment Spotted"
            ])
            activities.append({"Date": date, "Coordinate": f"{lat:.4f}, {lon:.4f}", "Detection": event})
    return activities

# --- 2. THE INFERENCE ENGINE ---
def analyze_temporal_threat(activity_logs, is_sensitive):
    # Rule: If it's not a sensitive zone, threat is always Low unless something major is found
    if not is_sensitive:
        return "Low", "Area classified as Non-Sensitive. No tactical threats identified."
        
    if not activity_logs:
        return "Low", "Routine Status. No significant changes detected."
    
    if len(activity_logs) >= 2:
        return "High", "Critical Infrastructure Growth. Recommend immediate Recon."
    return "Medium", "Anomalous Activity detected. Increase monitoring."

# --- 3. UI DASHBOARD ---
st.set_page_config(page_title="GEOINT Border Monitor", layout="wide", page_icon="🛰️")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛰️ Advanced GEOINT Satellite Monitor")
st.write(f"**Analyst:** Prashanth C | IIT Jodhpur")

# Define Key Border Sectors
sectors = {
    "Jodhpur/Western Border": [26.2389, 73.0243],
    "Pangong Tso (LAC)": [33.7439, 78.7523],
    "Galwan Valley": [34.7500, 78.2000]
}

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Satellite Surveillance Feed")
    selected_name = st.selectbox("Switch Sector:", list(sectors.keys()))
    start_coords = sectors[selected_name]
    
    # --- SATELLITE VIEW CONFIGURATION ---
    # We use Google Satellite tiles for a realistic defense look
    m = folium.Map(location=start_coords, zoom_start=14)
    
    google_satellite = folium.TileLayer(
        tiles = 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr = 'Google',
        name = 'Google Satellite',
        overlay = False,
        control = True
    ).add_to(m)
    
    folium.Marker(start_coords, popup=selected_name).add_to(m)
    map_data = st_folium(m, width="100%", height=550)

with col2:
    st.subheader("Intelligence Report")
    
    # Manual Override for Geofencing
    is_sensitive_zone = st.toggle("Classify as Sensitive/Border Zone?", value=True)
    
    if map_data['last_clicked']:
        lat, lon = map_data['last_clicked']['lat'], map_data['last_clicked']['lng']
        st.success(f"📍 GPS Lock: `{lat:.4f}, {lon:.4f}`")
    else:
        lat, lon = start_coords[0], start_coords[1]
        st.info("🛰️ Monitoring Sector Center")
    
    if st.button("Query Temporal Change Logs", use_container_width=True):
        logs = get_historical_activity(lat, lon, is_sensitive_zone)
        threat, action = analyze_temporal_threat(logs, is_sensitive_zone)
        
        if logs:
            st.table(pd.DataFrame(logs))
        
        st.write("---")
        st.subheader("Assessment")
        m1, m2 = st.columns(2)
        m1.metric("Threat Level", threat)
        
        if threat == "High":
            st.error(f"**Alert:** {action}")
        elif threat == "Medium":
            st.warning(f"**Advisory:** {action}")
        else:
            st.success(f"**Status:** {action}")

st.sidebar.info("The system now uses Geofencing. If 'Sensitive Zone' is toggled off, threats will appear as Low.")
