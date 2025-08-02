import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import io

# Set the page to wide mode
st.set_page_config(layout="wide")

st.title("BattleScape")

# Hardcoded data for historical battles
# We're using a string in CSV format and reading it with pandas
battle_data = """Battle,Year,Latitude,Longitude,War,Participants
Battle of Hastings,1066,50.912,-0.488,Norman conquest of England,"Normans, English"
Battle of Waterloo,1815,50.678,4.406,Napoleonic Wars,"French Empire, Seventh Coalition"
Battle of Gettysburg,1863,39.814,-77.232,American Civil War,"United States, Confederate States"
Battle of Stalingrad,1942,48.700,44.517,World War II,"Soviet Union, Nazi Germany"
Battle of Trafalgar,1805,36.250,-6.200,Napoleonic Wars,"United Kingdom, French and Spanish Navies"
Battle of Agincourt,1415,50.463,2.141,Hundred Years' War,"England, France"
Battle of Thermopylae,-480,38.795,22.561,Greco-Persian Wars,"Greek city-states, Persian Empire"
Battle of Midway,1942,28.208,-177.375,World War II,"United States, Empire of Japan"
Battle of Austerlitz,1805,49.150,16.767,Napoleonic Wars,"French Empire, Russian & Austrian Empires"
Battle of Cannae,-216,41.295,16.152,Second Punic War,"Carthage, Roman Republic"
Battle of Tours,732,47.394,0.685,Umayyad invasion of Gaul,"Frankish Kingdom, Umayyad Caliphate"
Battle of Yorktown,1781,37.239,-76.510,American Revolutionary War,"United States & France, Great Britain"
Battle of Marathon,-490,38.118,23.947,Greco-Persian Wars,"Athens, Persian Empire"
Battle of Actium,-31,38.955,20.766,Final War of the Roman Republic,"Octavian, Mark Antony & Cleopatra"
Battle of Dien Bien Phu,1954,21.383,103.017,First Indochina War,"Viet Minh, French Union"
Battle of Sekigahara,1600,35.361,136.467,Japanese unification,"Tokugawa Ieyasu, Ishida Mitsunari"
"""

# Read the string data into a pandas DataFrame
df = pd.read_csv(io.StringIO(battle_data))


# Create the map
# You can adjust the location and zoom_start to your preference
m = folium.Map(location=[45, 10], zoom_start=2) # Zoomed out slightly to see all points

# Add markers for each battle
for index, row in df.iterrows():
    # Create the popup text
    popup_text = f"""
    <b>Battle:</b> {row['Battle']}<br>
    <b>Date:</b> {row['Year']}<br>
    <b>War:</b> {row['War']}<br>
    <b>Participants:</b> {row['Participants']}
    """
    
    # Create the tooltip text
    tooltip_text = f"{row['Battle']} ({row['Year']})"

    # Add the marker to the map with a custom icon
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=folium.Popup(popup_text, max_width=300),
        tooltip=tooltip_text,
        icon=folium.Icon(color='darkred', icon='crosshairs', prefix='fa')
    ).add_to(m)

# Display the map in the Streamlit app
st_data = st_folium(m, width=1200, height=800)
