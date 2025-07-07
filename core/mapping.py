import folium
from folium.plugins import MarkerCluster

def create_map(accom_df, attr_df, start_lat = 35.68, start_lon=139.76, zoom = 12):
    fmap = folium.Map(location=[start_lat, start_lon], zoom_start = zoom)
    accom_cluster = MarkerCluster(name="Accomodations").add_to(fmap)
    attr_cluster = MarkerCluster(name="Attractions").add_to(fmap)


    for _, row in accom_df.iterrows():
         folium.Marker(
            [row.lat, row.lon],
            popup=folium.Popup(f"🏨 <b>{row["name"]}</b><br>¥{row.price}", max_width=250),
            icon=folium.Icon(color="blue", icon="home"),
        ).add_to(accom_cluster)
         
    for _, row in attr_df.iterrows():
        folium.Marker(
            [row.lat, row.lon],
            popup=folium.Popup(f"🎯 {row["name"]}", max_width=200),
            icon=folium.Icon(color="green", icon="info-sign"),
        ).add_to(attr_cluster)

    folium.LayerControl().add_to(fmap)
    return fmap 
    