import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium import plugins
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import base64
from io import BytesIO

st.set_page_config(layout="wide")
st.title("🧠 Oshibori Delivery Route Optimization Dashboard")

# Upload section
st.sidebar.header("📂 Upload Your Files")
uploaded_df = st.sidebar.file_uploader("Upload Geocoded Oshibori Data (CSV)", type="csv")
uploaded_routes_df = st.sidebar.file_uploader("Upload Optimized Routes (CSV)", type="csv")
uploaded_distance_matrix = st.sidebar.file_uploader("Upload Distance Matrix (.npy)", type="npy")
uploaded_duration_matrix = st.sidebar.file_uploader("Upload Duration Matrix (.npy)", type="npy")

# Day selector
selected_day = st.sidebar.selectbox("Select Delivery Day", ["Monday", "Wednesday", "Friday"])
st.sidebar.markdown(f"**Selected Day:** {selected_day}")

# Load data if all files uploaded
if uploaded_df and uploaded_routes_df and uploaded_distance_matrix and uploaded_duration_matrix:
    df = pd.read_csv(uploaded_df)
    routes_df = pd.read_csv(uploaded_routes_df)
    distance_matrix = np.load(uploaded_distance_matrix)
    duration_matrix = np.load(uploaded_duration_matrix)

    st.success("✅ Files successfully loaded!")

    # Route Viewer
    st.subheader("📋 Route Summary Table")
    vehicle_ids = routes_df['VehicleID'].unique().tolist()
    selected_vehicle = st.selectbox("Select a Vehicle to View its Route", vehicle_ids)

    filtered_route = routes_df[routes_df['VehicleID'] == selected_vehicle]
    st.dataframe(filtered_route.reset_index(drop=True))

    # Google Maps Link
    gmap_link = filtered_route.iloc[0]['GoogleMapsLink']
    if gmap_link:
        st.markdown(f"[📍 View Route on Google Maps]({gmap_link})", unsafe_allow_html=True)

    # Folium Map
    st.subheader("🗺️ Optimized Routes on Map")
    start_lat = df.iloc[0]['Latitude']
    start_lon = df.iloc[0]['Longitude']
    m = folium.Map(location=[start_lat, start_lon], zoom_start=13)

    color_list = [
        'red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue',
        'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen',
        'gray', 'black', 'lightgray'
    ]

    for vehicle_id in routes_df['VehicleID'].unique():
        vehicle_data = routes_df[routes_df['VehicleID'] == vehicle_id]
        coords = []
        for _, row in vehicle_data.iterrows():
            store = df[df['StoreName'] == row['StoreName']]
            if not store.empty:
                coords.append((store.iloc[0]['Latitude'], store.iloc[0]['Longitude']))

        if coords:
            color = color_list[vehicle_id % len(color_list)]
            folium.PolyLine(coords, color=color, weight=5, opacity=0.8, tooltip=f'Vehicle {vehicle_id}').add_to(m)
            for lat, lon in coords:
                folium.CircleMarker(location=(lat, lon), radius=4, color=color, fill=True, fill_color=color).add_to(m)

    st_data = st_folium(m, width=1000)

    # Matplotlib Plot
    st.subheader("📍 Route Overview (Scatter Plot)")
    fig, ax = plt.subplots(figsize=(10, 8))

    for vehicle_id in routes_df['VehicleID'].unique():
        vehicle_data = routes_df[routes_df['VehicleID'] == vehicle_id]
        coords = []
        for _, row in vehicle_data.iterrows():
            store = df[df['StoreName'] == row['StoreName']]
            if not store.empty:
                coords.append((store.iloc[0]['Longitude'], store.iloc[0]['Latitude']))

        if coords:
            coords = np.array(coords)
            ax.plot(coords[:, 0], coords[:, 1], marker='o', label=f'Vehicle {vehicle_id}')

    ax.set_title('Optimized Vehicle Routes')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

else:
    st.warning("⚠️ Please upload all required files from the sidebar to continue.")
