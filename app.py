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
"""

# Read the string data into a pandas DataFrame
df = pd.read_csv(io.StringIO(battle_data))


# Create the map
# You can adjust the location and zoom_start to your preference
m = folium.Map(location=[45, 10], zoom_start=3)

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

    # Add the marker to the map
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=folium.Popup(popup_text, max_width=300),
        tooltip=tooltip_text
    ).add_to(m)

# Display the map in the Streamlit app
st_data = st_folium(m, width=1200, height=800)
