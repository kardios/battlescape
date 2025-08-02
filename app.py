import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import io

# Set the page to wide mode
st.set_page_config(layout="wide")

st.title("BattleScape")

# Hardcoded data for historical battles, now with a Battle_Type column
# We're using a string in CSV format and reading it with pandas
battle_data = """Battle,Year,Latitude,Longitude,War,Participants,Battle_Type
Battle of Hastings,1066,50.912,-0.488,Norman conquest of England,"Normans, English",Pitched Battle
Battle of Waterloo,1815,50.678,4.406,Napoleonic Wars,"French Empire, Seventh Coalition",Pitched Battle
Battle of Gettysburg,1863,39.814,-77.232,American Civil War,"United States, Confederate States",Pitched Battle
Battle of Antietam,1862,39.473,-77.749,American Civil War,"United States, Confederate States",Pitched Battle
Battle of Shiloh,1862,35.149,-88.322,American Civil War,"United States, Confederate States",Pitched Battle
Siege of Vicksburg,1863,32.339,-90.878,American Civil War,"United States, Confederate States",Siege
Battle of Stalingrad,1942,48.700,44.517,World War II,"Soviet Union, Nazi Germany",Siege
Battle of Trafalgar,1805,36.250,-6.200,Napoleonic Wars,"United Kingdom, French and Spanish Navies",Naval
Battle of Agincourt,1415,50.463,2.141,Hundred Years' War,"England, France",Pitched Battle
Battle of Thermopylae,-480,38.795,22.561,Greco-Persian Wars,"Greek city-states, Persian Empire",Pitched Battle
Battle of Salamis,-480,37.952,23.568,Greco-Persian Wars,"Greek city-states, Persian Empire",Naval
Battle of Plataea,-479,38.216,23.279,Greco-Persian Wars,"Greek city-states, Persian Empire",Pitched Battle
Battle of Midway,1942,28.208,-177.375,World War II,"United States, Empire of Japan",Naval
Battle of Austerlitz,1805,49.150,16.767,Napoleonic Wars,"French Empire, Russian & Austrian Empires",Pitched Battle
Battle of Cannae,-216,41.295,16.152,Second Punic War,"Carthage, Roman Republic",Pitched Battle
Battle of Zama,-202,36.08,9.45,Second Punic War,"Roman Republic, Carthage",Pitched Battle
Battle of Alesia,-52,47.53,4.49,Gallic Wars,"Roman Republic, Gallic Tribes",Siege
Battle of Tours,732,47.394,0.685,Umayyad invasion of Gaul,"Frankish Kingdom, Umayyad Caliphate",Pitched Battle
Battle of Yorktown,1781,37.239,-76.510,American Revolutionary War,"United States & France, Great Britain",Siege
Battle of Marathon,-490,38.118,23.947,Greco-Persian Wars,"Athens, Persian Empire",Pitched Battle
Battle of Actium,-31,38.955,20.766,Final War of the Roman Republic,"Octavian, Mark Antony & Cleopatra",Naval
Battle of Dien Bien Phu,1954,21.383,103.017,First Indochina War,"Viet Minh, French Union",Siege
Battle of Mang Yang Pass,1954,14.01,108.45,First Indochina War,"French Union, Viet Minh",Guerilla Action
Battle of Ia Drang,1965,13.65,107.68,Vietnam War,"United States & South Vietnam, North Vietnam",Pitched Battle
Battle of Khe Sanh,1968,16.62,106.72,Vietnam War,"United States & South Vietnam, North Vietnam",Siege
Battle of Hue,1968,16.46,107.59,Vietnam War,"United States & South Vietnam, North Vietnam",Pitched Battle
Battle of Sekigahara,1600,35.361,136.467,Sengoku period,"Tokugawa Ieyasu, Ishida Mitsunari",Pitched Battle
Battle of Okehazama,1560,35.06,136.95,Sengoku period,"Oda clan, Imagawa clan",Pitched Battle
Battle of Nagashino,1575,34.97,137.69,Sengoku period,"Oda-Tokugawa alliance, Takeda clan",Pitched Battle
4th Battle of Kawanakajima,1561,36.58,138.18,Sengoku period,"Takeda clan, Uesugi clan",Pitched Battle
Battle of the Somme,1916,49.99,2.65,World War I,"Allied Powers, Central Powers",Pitched Battle
Battle of Verdun,1916,49.16,5.38,World War I,"France, German Empire",Pitched Battle
Battle of Gallipoli,1915,40.24,26.28,World War I,"Ottoman Empire, Allied Powers",Amphibious Assault
Siege of Jerusalem,1099,31.77,35.22,First Crusade,"Crusaders, Fatimid Caliphate",Siege
Battle of Hattin,1187,32.79,35.44,Crusades,"Ayyubid Sultanate, Kingdom of Jerusalem",Pitched Battle
Siege of Baghdad,1258,33.34,44.40,Mongol Invasions,"Mongol Empire, Abbasid Caliphate",Siege
Battle of Legnica,1241,51.15,16.16,Mongol Invasions,"Mongol Empire, European Alliance",Pitched Battle
Battle of Red Cliffs,208,29.89,113.60,Three Kingdoms Period,"Sun-Liu alliance, Cao Cao",Naval
Battle of Ayacucho,1824,-13.16,-74.22,Peruvian War of Independence,"Peruvian & Gran Colombian forces, Spanish Empire",Pitched Battle
Battle of Isandlwana,1879,-28.35,30.65,Anglo-Zulu War,"Zulu Kingdom, British Empire",Pitched Battle
Castle Hill Rebellion,1804,-33.74,150.96,Australian colonial history,"Irish convicts, British colonial forces",Guerilla Action
"""

# Read the string data into a pandas DataFrame
df = pd.read_csv(io.StringIO(battle_data))

# --- Sidebar for Filters ---
st.sidebar.header("Filter Battles")

# War filter
war_list = ['All Wars'] + sorted(df['War'].unique())
selected_war = st.sidebar.selectbox('Select a War:', war_list)

# Year filter
min_year = int(df['Year'].min())
max_year = int(df['Year'].max())
selected_years = st.sidebar.slider(
    'Select a Year Range:',
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# --- Data Filtering ---
# Filter by war
if selected_war == 'All Wars':
    filtered_df = df
else:
    filtered_df = df[df['War'] == selected_war]

# Filter by year range
filtered_df = filtered_df[
    (filtered_df['Year'] >= selected_years[0]) & (filtered_df['Year'] <= selected_years[1])
]


# --- Map Creation ---

# Define a mapping from Battle_Type to a Font Awesome icon
icon_map = {
    'Naval': 'anchor',
    'Siege': 'university',  # Represents a fortified building/city
    'Pitched Battle': 'shield-alt',
    'Guerilla Action': 'fire',
    'Amphibious Assault': 'ship'
}
default_icon = 'crosshairs'

# Create the map
if not filtered_df.empty:
    map_center = [filtered_df['Latitude'].mean(), filtered_df['Longitude'].mean()]
    zoom_start = 5 if len(filtered_df['War'].unique()) == 1 and selected_war != 'All Wars' else 2
else:
    map_center = [20, 0]
    zoom_start = 2
    st.warning("No battles found for the selected filters.")

m = folium.Map(location=map_center, zoom_start=zoom_start, tiles='CartoDB Positron')

# Add markers for each battle
if not filtered_df.empty:
    for index, row in filtered_df.iterrows():
        # Get the icon for the battle type, or use the default
        icon_name = icon_map.get(row['Battle_Type'], default_icon)
        
        popup_text = f"""
        <b>Battle:</b> {row['Battle']}<br>
        <b>Date:</b> {row['Year']}<br>
        <b>War:</b> {row['War']}<br>
        <b>Type:</b> {row['Battle_Type']}<br>
        <b>Participants:</b> {row['Participants']}
        """
        
        tooltip_text = f"{row['Battle']} ({row['Year']})"

        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=tooltip_text,
            icon=folium.Icon(color='darkred', icon=icon_name, prefix='fa')
        ).add_to(m)

# Display the map
st_data = st_folium(m, width=1200, height=800)
