import streamlit as st
import pandas as pd
from core import distance, scoring, mapping, coord_parser, geocoder
from streamlit_folium import st_folium
from core.db import create_tables, insert_city, insert_accomodation, insert_attraction, get_connection

st.set_page_config(page_title="accom. picker", page_icon="📌")

# setup for database
create_tables()

# sidebar
st.sidebar.title("Settings")
nearby_radius_km = st.sidebar.slider("Nearby radius (km)", 0.5, 5.0, 2.0, 0.5)
city_name = st.sidebar.text_input("Enter city name", value = "Tokyo")

if not city_name.strip():
    st.warning("Please enter a city name to proceed.")
    st.stop()

city_id = insert_city(city_name)

# attractions (form and registering information)
st.header("Attractions")

with st.form("attraction_form"):
    name_or_address = st.text_input("Attraction Name or Address")
    submitted = st.form_submit_button("Add Attraction")

    if submitted and name_or_address:
        with st.spinner("Geocoding..."):
            latlon = geocoder.geocode(name_or_address)
        
        if latlon:
            st.write(city_id)
            insert_attraction(name_or_address, latlon[0], latlon[1], city_id)
            st.success(f"Added {name_or_address} at {latlon}")
        else:
            st.error("Could not geocode the provided name or address.")

conn = get_connection()
attr_df = pd.read_sql_query("""
                                   SELECT name, lat, lon FROM attractions
                                   WHERE city_id = ? """, conn, params=(city_id,))
conn.close()
st.dataframe(attr_df)


# accomodations (form and registering information)
st.header("Accommodations")

with st.form("accommodation_form"):
    name_or_address = st.text_input("Accommodation Name or Address")
    price = st.number_input("Price (€)", 0, 1000000, 100, step=500)
    submitted = st.form_submit_button("Add Accommodation")

    if submitted and name_or_address:
        with st.spinner("Geocoding..."):
            latlon = geocoder.geocode(name_or_address)

        if latlon:
            insert_accomodation(name_or_address, latlon[0], latlon[1], price, city_id)
            st.success(f"Added {name_or_address} at {latlon}")
        else:
            st.warning("Could not geocode that name or address.")

conn = get_connection()
accom_df = pd.read_sql_query("""
    SELECT name, lat, lon, price FROM accomodations
    WHERE city_id = ?
""", conn, params=(city_id,))
conn.close()

if not accom_df.empty:
    st.success(f"{len(accom_df)} accommodation(s) stored for {city_name}.")
    st.dataframe(accom_df)

# analysis of data and results on map

if not accom_df.empty and not attr_df.empty:
    st.header("Analysis")

    results = []
    for _, accom in accom_df.iterrows():
        dists = attr_df.apply(
            lambda attr: distance.haversine(accom.lat, accom.lon, attr.lat, attr.lon), axis = 1
        )
        nearest_idx = dists.idxmin()
        nearby_count = (dists <= nearby_radius_km).sum()
        nearest_dist = round(dists.min(), 2)

        score = scoring.default_score(nearest_dist, accom.price, nearby_count)

        results.append({
            "Accomodation" : accom["name"],
            "Price (€)": accom.price,
            "Nearest Attraction": attr_df.loc[nearest_idx, "name"],
            "Distance (km)": nearest_dist,
            f"Attractions ≤ {nearby_radius_km} km": nearby_count,
            "Score": score
        })

    res_df = pd.DataFrame(results)
    sort_by = st.selectbox("Sort by", res_df.columns, index = res_df.columns.get_loc("Score"))
    st.dataframe(res_df.sort_values(sort_by, ascending = sort_by not in ["Score"]))

    # map
    st.header("Map")
    fmap = mapping.create_map(accom_df, attr_df)
    st_folium(fmap, use_container_width=True)

else:
    st.info("Please add at least one attraction and one accomodation to begin.")
