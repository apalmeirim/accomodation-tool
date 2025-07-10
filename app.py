# app.py
import streamlit as st
import pandas as pd
from core import distance, scoring, mapping, auth, db
from streamlit_folium import st_folium

st.set_page_config(page_title="Accommodation Picker", page_icon="")

# Authentication
st.sidebar.header("Login / Signup")

auth_mode = st.sidebar.radio("Choose mode:", ["Login", "Signup"])
email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")

if auth_mode == "Login" and st.sidebar.button("Login"):
    user = auth.login_user(email, password)
    if user:
        st.session_state["user"] = user
    else:
        st.error("Login failed.")

elif auth_mode == "Signup" and st.sidebar.button("Signup"):
    user = auth.signup_user(email, password)
    if user:
        st.session_state["user"] = user
    else:
        st.error("Signup failed.")

user = st.session_state.get("user", auth.get_current_user())
if not user:
    st.stop()

st.success(f"Welcome, {user.email}")

# dataload
attractions = db.get_user_entries("attractions", user.id)
accommodations = db.get_user_entries("accommodations", user.id)

# add attrac.
st.header("Add Attractions")
with st.form("attraction_form"):
    name = st.text_input("Attraction Name")
    coord_input = st.text_input("Coordinates (e.g., 35.6895, 139.6917)")
    if st.form_submit_button("Add Attraction") and name and coord_input:
        try:
            lat, lon = map(float, coord_input.split(","))
            db.insert_attraction("attractions", user.id, {"name": name, "lat": lat, "lon": lon})
            st.rerun()
        except:
            st.warning("Invalid coordinate format.")

# add accomm.
st.header("Add Accommodations")
with st.form("accommodation_form"):
    name = st.text_input("Accommodation Name")
    coord_input = st.text_input("Coordinates (e.g., 35.6895, 139.6917)", key="accom_coords")
    price = st.number_input("Price (€)", 0, 100000, 10000, step=500)
    if st.form_submit_button("Add Accommodation") and name and coord_input:
        try:
            lat, lon = map(float, coord_input.split(","))
            db.insert_accommodation("accommodations", user.id, {
                "name": name, "lat": lat, "lon": lon, "price": price
            })
            st.rerun()
        except:
            st.warning("Invalid coordinate format.")

# tables
if attractions:
    st.subheader("🗺️ Attractions")
    st.dataframe(pd.DataFrame(attractions))

if accommodations:
    st.subheader("🏠 Accommodations")
    st.dataframe(pd.DataFrame(accommodations))

# analysis
if attractions and accommodations:
    st.header("📊 Analysis")
    radius_km = st.sidebar.slider("Nearby radius (km)", 0.5, 5.0, 2.0, 0.5)

    accom_df = pd.DataFrame(accommodations)
    attr_df = pd.DataFrame(attractions)

    results = []
    for _, accom in accom_df.iterrows():
        dists = attr_df.apply(
            lambda attr: distance.haversine(accom.lat, accom.lon, attr.lat, attr.lon), axis=1
        )
        nearest_idx = dists.idxmin()
        nearby_count = (dists <= radius_km).sum()
        nearest_dist = round(dists.min(), 2)
        score = scoring.default_score(nearest_dist, accom.price, 0, nearby_count)  # No rating

        results.append({
            "Accommodation": accom["name"],
            "Price (¥)": accom["price"],
            "Nearest Attraction": attr_df.loc[nearest_idx, "name"],
            "Distance (km)": nearest_dist,
            f"Attractions ≤ {radius_km} km": nearby_count,
            "Score": score
        })

    res_df = pd.DataFrame(results)
    sort_by = st.selectbox("Sort by", res_df.columns, index=res_df.columns.get_loc("Score"))
    st.dataframe(res_df.sort_values(sort_by, ascending=sort_by not in ["Score"]))

    # map
    st.header("🗺️ Map")
    fmap = mapping.create_map(accom_df, attr_df)
    st_folium(fmap, use_container_width=True)

else:
    st.info("Please add at least one attraction and one accommodation to begin.")