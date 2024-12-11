import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os
import json
from dotenv import load_dotenv
current_path = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_path, "..", "images", "logo.jpg")
st.image(image_path, caption="Repair Shop Recommendations Based on Fault Location", use_column_width=True)


# Load environment variables such as MAPBOX_TOKEN
load_dotenv()
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")

# Backend API URL (modify according to actual deployment)
API_BASE_URL = "http://127.0.0.1:5000"

st.title("Best Auto Repair📍")
st.write("---")

# Fetch fault parts list from the backend
fault_parts = []
try:
    response = requests.get(f"{API_BASE_URL}/api/fault-parts")
    if response.status_code == 200:
        data = response.json()
        fault_parts = data.get("fault_parts", [])
    else:
        st.error(f"Failed to retrieve the list of fault parts. Status code: {response.status_code}")
except Exception as e:
    st.error(f"Error while retrieving fault parts: {e}")

col1, col2 = st.columns(2)

with col1:
    # Use a relative path for the image
    st.image(
    "/images/logo.jpg", 
    caption="Repair Shop Recommendations Based on Fault Location", 
    use_column_width=True
)


with col2:
    st.subheader("JUST SEARCH HERE!🌟 ")
    with st.form(key="my_form"):
        selected_fault = st.selectbox("Select fault part (optional)", [""] + fault_parts)
        user_input = st.text_input("No specific fault part? Enter a description and we will recommend suitable shops!")

        # Combine latitude and longitude input into a single location input
        user_location = st.text_input("Enter your location (optional).")

        submit_button = st.form_submit_button("Search")

st.write("---")

if submit_button:
    try:
        query_params = {}
        # Determine whether to use fault_id or query_text
        if selected_fault.strip():
            query_params["fault_id"] = selected_fault.strip()
        elif user_input.strip():
            query_params["query_text"] = user_input.strip()
        else:
            st.warning("Please provide at least a fault part or a description!")
            st.stop()

        # Parse user location input
        if user_location.strip():
            try:
                lat_lon = user_location.strip().split(",")
                if len(lat_lon) == 2:
                    query_params["user_lat"] = float(lat_lon[0].strip())
                    query_params["user_lon"] = float(lat_lon[1].strip())
                else:
                    st.warning("Invalid location format. Please provide coordinates as 'latitude, longitude'. Ignoring location information.")
            except ValueError:
                st.warning("Invalid location input. Ignoring location information.")

        recommend_url = f"{API_BASE_URL}/api/recommend"
        response = requests.get(recommend_url, params=query_params)

        if response.status_code == 200:
            result_data = response.json()
            businesses = result_data.get("businesses", [])

            if not businesses:
                st.write("No matching shops found. Please try another fault part or description.")
            else:
                st.subheader("Recommended shops for you:")

                df_list = []
                for b in businesses:
                    geom_json = b.get("geom")
                    if geom_json:
                        try:
                            geom = json.loads(geom_json)
                            coords = geom.get("coordinates", [None, None])
                            longitude, latitude = coords[0], coords[1]
                        except (json.JSONDecodeError, TypeError, IndexError):
                            longitude, latitude = None, None
                    else:
                        longitude, latitude = None, None

                    df_list.append({
                        "name": b.get("name", "N/A"),
                        "stars": b.get("stars", "N/A"),
                        "address": b.get("address", "N/A"),
                        "longitude": longitude,
                        "latitude": latitude
                    })

                restaurants_df = pd.DataFrame(df_list)

                # Display shop information
                if not restaurants_df.empty:
                    for idx, row in restaurants_df.iterrows():
                        st.markdown(f"**Shop Name:** {row['name']}")
                        st.markdown(f"**Rating:** {row['stars']}")
                        st.markdown(f"**Address:** {row['address']}")
                        st.write("---")
                else:
                    st.write("No shop data found.")

                # Display the map
                if not restaurants_df.empty and "latitude" in restaurants_df.columns and "longitude" in restaurants_df.columns:
                    map_df = restaurants_df.dropna(subset=["latitude", "longitude"])
                    if not map_df.empty and MAPBOX_TOKEN:
                        px.set_mapbox_access_token(MAPBOX_TOKEN)
                        fig = px.scatter_mapbox(
                            map_df,
                            lon="longitude",
                            lat="latitude",
                            hover_name="name",
                            hover_data=["address", "stars"],
                            color_discrete_sequence=["rgba(255, 165, 0, 0.9)"],
                            zoom=10,
                            size_max=20,  # Enlarge the points for better visibility
                            title="Distribution of Shop Locations"
                        )
                        st.plotly_chart(fig)
                    elif not MAPBOX_TOKEN:
                        st.warning("Mapbox Token is not set. Unable to display the map.")
                    else:
                        st.write("No valid geographic data available. Cannot display the map.")
        else:
            # Non-200 status code from the backend
            try:
                err_data = response.json()
                st.error(f"Request failed: {err_data.get('error', 'Unknown error')}")
            except:
                st.error(f"Request failed with status code: {response.status_code}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
