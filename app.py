import streamlit as st
from streamlit_folium import st_folium
import folium
import random
import pandas as pd
from datetime import datetime, timedelta

# --- 1. MOCK TEMPORAL DATA GENERATOR ---
def get_historical_activity(lat, lon):
    activities = []
    # Seed randomness so a specific coordinate always gives consistent "mock" results
    random.seed(int(lat * 1000) + int(lon * 1000)) 
    
    for i in range(3):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        if random.random() > 0.4:
            event = random.choice([
                "New Concrete Foundation (Bunker Type)", 
                "Metallic Cluster (Possible Convoy)", 
                "Trench Extension Detected",
                "Earth Moving Equipment Spotted",
                "Surface-to-Air Battery Signature"
            ])
            activities.append({
                "Date": date, 
                "Coordinate": f"{lat:.4f}, {lon:.4f}", 
                "Detection": event
            })
    return activities

# --- 2. THE INFERENCE ENGINE (Logic for History) ---
def analyze_temporal_threat(activity_logs):
    if not activity_logs:
        return "Low", "Routine Status. No significant changes detected in the 72h window."
    
    if len(activity_logs) >= 2:
        return "High", "Critical Infrastructure Growth. Recommend immediate Satellite Tasking or Drone Recon."
    return "Medium", "Anomalous Activity detected. Increase monitoring frequency for this sector."

# --- 3. UI DASHBOARD ---
st.set_page_config(page_title="GEOINT Border Monitor", layout="wide", page_icon="🛰️")

# Corrected Custom CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    </style>
    """, unsafe_allow_html=True) # FIXED PARAMETER HERE

st.title("🛰️ Border Activity Monitoring System (Temporal)")
st.write(f"**Surveillance Dashboard** | Analyst: Prashanth C | IIT Jodhpur")

# Define Key Border Sectors (Lat, Lon)
sectors = {
    "Jodhpur/Western Border": [26.2389, 73.0243],
    "Pangong Tso (LAC)": [33.7439, 78.7523],
    "Galwan Valley": [34.7500, 78.2000],
    "Naku La Sector": [28.0167, 88.5833]
}

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Interactive Satellite Mapping")
    selected_name = st.selectbox("Quick-Jump to Sector:", list(sectors.keys()))
    start_coords = sectors[selected_name]
    
    # Initialize Folium Map
    m = folium.Map(location=start_coords, zoom_start=12, control_scale=True)
    
    # Add a marker for the current center
    folium.Marker(
        start_coords, 
        popup=f"Primary Monitoring Station: {selected_name}",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)
    
    # Capture map clicks
    map_data = st_folium(m, width="100%", height=550)

with col2:
    st.subheader("Intelligence Report")
    
    if map_data['last_clicked']:
        lat = map_data['last_clicked']['lat']
        lon = map_data['last_clicked']['lng']
        st.success(f"📍 GPS Lock: `{lat:.4f}, {lon:.4f}`")
    else:
        lat, lon = start_coords[0], start_coords[1]
        st.info(f"🛰️ Defaulting to Sector Center: `{lat:.4f}, {lon:.4f}`")
    
    st.write("---")
    
    if st.button("Query Temporal Change Logs", use_container_width=True):
        with st.spinner("Accessing Historical Archives..."):
            import time
            time.sleep(1) 
            
            logs = get_historical_activity(lat, lon)
            threat, action = analyze_temporal_threat(logs)
            
            if logs:
                st.write("**Recent Detections (Last 72h):**")
                st.table(pd.DataFrame(logs))
            else:
                st.info("Zero anomalies found at these coordinates in the current window.")
            
            st.write("---")
            st.subheader("Threat Assessment")
            
            m1, m2 = st.columns(2)
            m1.metric("Current Level", threat)
            
            if threat == "High":
                st.error(f"**Alert:** {action}")
            elif threat == "Medium":
                st.warning(f"**Advisory:** {action}")
            else:
                st.success(f"**Status:** {action}")

st.sidebar.markdown("### System Diagnostics")
st.sidebar.write("API Status: Connected ✅")
st.sidebar.write(f"Last Sync: {datetime.now().strftime('%H:%M:%S')}")
st.sidebar.markdown("---")
st.sidebar.info("Click anywhere on the map to query specific geographic coordinates for temporal changes.")
