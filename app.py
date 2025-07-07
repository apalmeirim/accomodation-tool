import streamlit as st
import pandas as pd
from core import distance, scoring, mapping, coord_parser
from streamlit_folium import st_folium

st.set_page_config(page_title="Accommodation Picker", page_icon="🎌")

# Session state init
if "attractions" not in st.session_state:
    st.session_state.attractions = []
if "accommodations" not in st.session_state:
    st.session_state.accommodations = []

# Sidebar
st.sidebar.title("Settings")
nearby_radius_km = st.sidebar.slider("Nearby radius (km)", 0.5, 5.0, 2.0, 0.5)

# --- Add ATTRACTIONS ----------------------------------------------------------------
st.header("🎯 Tourist Attractions")

with st.form("attraction_form"):
    name = st.text_input("Attraction Name")
    coord_str = st.text_input("Coordinates (paste from Google)", key="attr_coord")
    submitted = st.form_submit_button("Add Attraction")

    if submitted and name and coord_str:
        latlon = coord_parser.parse(coord_str)
        if latlon:
            st.session_state.attractions.append({
                "name": name,
                "lat": latlon[0],
                "lon": latlon[1]
            })
        else:
            st.warning("Could not parse those coordinates.")


if st.session_state.attractions:
    st.success(f"{len(st.session_state.attractions)} attraction(s) added.")
    st.dataframe(pd.DataFrame(st.session_state.attractions))

# --- Add ACCOMMODATIONS -------------------------------------------------------------
st.header("🏨 Accommodations")

with st.form("accommodation_form"):
    name = st.text_input("Accommodation Name")
    coord_str = st.text_input("Coordinates (paste from Google)", key="accom_coord")
    price = st.number_input("Price (€)", 0, 1000000, 100, step=500)
    submitted = st.form_submit_button("Add Accommodation")

    if submitted and name and coord_str:
        latlon = coord_parser.parse(coord_str)
        if latlon:
            st.session_state.accommodations.append({
                "name": name,
                "lat": latlon[0],
                "lon": latlon[1],
                "price": price
            })
        else:
            st.warning("Could not parse those coordinates.")

if st.session_state.accommodations:
    st.success(f"{len(st.session_state.accommodations)} accommodation(s) added.")
    st.dataframe(pd.DataFrame(st.session_state.accommodations))

# --- Analysis and Results ----------------------------------------------------------
if st.session_state.attractions and st.session_state.accommodations:
    st.header("📊 Analysis")

    accom_df = pd.DataFrame(st.session_state.accommodations)
    attr_df = pd.DataFrame(st.session_state.attractions)

    results = []
    for _, accom in accom_df.iterrows():
        dists = attr_df.apply(
            lambda attr: distance.haversine(accom.lat, accom.lon, attr.lat, attr.lon), axis=1
        )
        nearest_idx = dists.idxmin()
        nearby_count = (dists <= nearby_radius_km).sum()
        nearest_dist = round(dists.min(), 2)

        # Update scoring function if needed (remove rating dependency)
        score = scoring.default_score(nearest_dist, accom.price, nearby_count)

        results.append({
            "Accommodation": accom["name"],
            "Price (€)": accom.price,
            "Nearest Attraction": attr_df.loc[nearest_idx, "name"],
            "Distance (km)": nearest_dist,
            f"Attractions ≤ {nearby_radius_km} km": nearby_count,
            "Score": score
        })

    res_df = pd.DataFrame(results)
    sort_by = st.selectbox("Sort by", res_df.columns, index=res_df.columns.get_loc("Score"))
    st.dataframe(res_df.sort_values(sort_by, ascending=sort_by not in ["Score"]))

    # Map
    st.header("🗺️ Map")
    fmap = mapping.create_map(accom_df, attr_df)
    st_folium(fmap, use_container_width=True)

else:
    st.info("Please add at least one attraction and one accommodation to begin.")
