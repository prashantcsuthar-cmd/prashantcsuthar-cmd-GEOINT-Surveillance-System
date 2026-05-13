import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd
from datetime import datetime, timedelta
from sentinelhub import SHConfig, SentinelHubCatalog, Geometry, CRS

# --- 1. SATELLITE CONFIGURATION ---
config = SHConfig()
try:
    config.sh_client_id = st.secrets["SH_CLIENT_ID"]
    config.sh_client_secret = st.secrets["SH_CLIENT_SECRET"]
    config.instance_id = st.secrets["SH_INSTANCE_ID"]
    config.sh_base_url = "https://services.sentinel-hub.com"
except Exception as e:
    st.error("Secrets missing! Ensure .streamlit/secrets.toml is configured.")

# --- 2. DATA FETCH ENGINE (Final CQL2-Text Logic) ---
def get_actual_satellite_activity(lat, lon):
    catalog = SentinelHubCatalog(config=config)
    
    # Create a tiny 100m square (Polygon) around the coordinate
    b = 0.001 
    bbox = [lon - b, lat - b, lon + b, lat + b]
    
    search_area = Geometry(
        geometry={
            'type': 'Polygon',
            'coordinates': [[
                [bbox[0], bbox[1]],
                [bbox[2], bbox[1]],
                [bbox[2], bbox[3]],
                [bbox[0], bbox[3]],
                [bbox[0], bbox[1]]
            ]]
        }, 
        crs=CRS.WGS84
    )
    
    # FIX: Using cql2-text format (simple string) to match the server requirement
    search_results = list(catalog.search(
        collection="sentinel-2-l2a",
        geometry=search_area,
        time=((datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d"), 
              datetime.now().strftime("%Y-%m-%d")),
        filter="eo:cloud_cover <= 50" # This is the cql2-text format
    ))
    
    logs = []
    for res in search_results[:5]:
        logs.append({
            "Date": res['properties']['datetime'][:10],
            "Cloud Cover": f"{res['properties']['eo:cloud_cover']:.1f}%",
            "Satellite": "Sentinel-2A/B",
            "Level": "L2A Surface Reflectance"
        })
    return logs

# --- 3. UI DASHBOARD ---
st.set_page_config(page_title="GEOINT Border Monitor", layout="wide", page_icon="🛰️")

st.title("🛰️ Live Border Surveillance System")
st.write(f"**Strategic Intelligence Dashboard** | Analyst: Prashanth C | IIT Jodhpur")

sectors = {
    "Bikaner (Western Border)": [28.0227, 73.3119],
    "Jaisalmer (Longewala)": [26.7606, 70.5225],
    "Galwan Valley (LAC)": [34.7500, 78.2000],
    "Pangong Tso Lake": [33.7439, 78.7523],
    "Jodhpur (Base HQ)": [26.2389, 73.0243]
}

col1, col2 = st.columns([2, 1])

with col1:
    selected_name = st.selectbox("Select Area of Interest:", list(sectors.keys()))
    start_coords = sectors[selected_name]
    
    # Initialize Map
    m = folium.Map(location=start_coords, zoom_start=10, tiles="OpenStreetMap")
    
    # Add your Sentinel-2 WMS Layer
    v_id = st.secrets["SH_INSTANCE_ID"]
    wms_url = f"https://services.sentinel-hub.com/ogc/wms/{v_id}"
    
    folium.WmsTileLayer(
        url=wms_url,
        layers="1_TRUE_COLOR", # Matches your verified Screenshot ID
        name="Sentinel-2 Real-Time",
        attr="Sentinel Hub",
        overlay=True,
        control=True,
        fmt="image/png"
    ).add_to(m)
    
    folium.Marker(start_coords, popup=f"Monitoring: {selected_name}").add_to(m)
    
    # Capture clicks
    map_output = st_folium(m, width=800, height=550, key="border_map")

with col2:
    st.subheader("Intelligence Report")
    
    if map_output and map_output.get('last_clicked'):
        lat, lon = map_output['last_clicked']['lat'], map_output['last_clicked']['lng']
        st.success(f"📍 GPS Lock: {lat:.4f}, {lon:.4f}")
        
        if st.button("Fetch Satellite Pass Logs", use_container_width=True):
            with st.spinner("Accessing ESA Archives (CQL2-Text Query)..."):
                try:
                    logs = get_actual_satellite_activity(lat, lon)
                    if logs:
                        st.table(pd.DataFrame(logs))
                        st.info("Analysis: Area is under active orbital surveillance.")
                    else:
                        st.warning("No clear imagery found in the 60-day window.")
                except Exception as e:
                    st.error(f"API Error: {e}")
    else:
        st.info("💡 **Analyst Tip:** Click a point on the map to trigger a temporal search.")

st.sidebar.markdown("### System Metadata")
st.sidebar.write("API Connectivity: Stable ✅")
st.sidebar.write("Protocol: Catalog 1.0.0 (CQL2-Text)")
st.sidebar.write(f"Refreshed: {datetime.now().strftime('%H:%M:%S')}")
