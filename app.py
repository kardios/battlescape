import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import io

# Set the page to wide mode
st.set_page_config(layout="wide")

st.title("BattleScape")

# Hardcoded data for historical battles, now with the full, ideal data structure.
# We're using a string in CSV format and reading it with pandas.
# Note: Using '|' as a separator because some descriptions contain commas.
battle_data = """Battle|Year|Latitude|Longitude|War|Battle_Type|Description|Belligerents_A|Belligerents_B|Commanders_A|Commanders_B|Result|Wiki_URL
Battle of Hastings|1066|50.912|-0.488|Norman conquest of England|Pitched Battle|Decisive Norman victory that led to the conquest of England.|Normans|English|William the Conqueror|King Harold Godwinson|Decisive Norman victory|https://en.wikipedia.org/wiki/Battle_of_Hastings
Battle of Waterloo|1815|50.678|4.406|Napoleonic Wars|Pitched Battle|Final defeat of Napoleon Bonaparte, ending his rule as Emperor of the French.|United Kingdom, Prussia, Netherlands|French Empire|Duke of Wellington, Blücher|Napoleon Bonaparte|Decisive Coalition victory|https://en.wikipedia.org/wiki/Battle_of_Waterloo
Battle of Gettysburg|1863|39.814|-77.232|American Civil War|Pitched Battle|Turning point of the American Civil War, ending Lee's invasion of the North.|United States|Confederate States|George Meade|Robert E. Lee|Decisive Union victory|https://en.wikipedia.org/wiki/Battle_of_Gettysburg
Siege of Vicksburg|1863|32.339|-90.878|American Civil War|Siege|Gave the Union control of the Mississippi River, a critical strategic goal.|United States|Confederate States|Ulysses S. Grant|John C. Pemberton|Decisive Union victory|https://en.wikipedia.org/wiki/Siege_of_Vicksburg
Battle of Stalingrad|1942|48.700|44.517|World War II|Siege|Major turning point on the Eastern Front of World War II.|Soviet Union|Nazi Germany, Romania, Italy|Georgy Zhukov|Friedrich Paulus|Decisive Soviet victory|https://en.wikipedia.org/wiki/Battle_of_Stalingrad
Battle of Trafalgar|1805|36.250|-6.200|Napoleonic Wars|Naval|Ensured British naval supremacy for over a century.|United Kingdom|French Empire, Spanish Empire|Horatio Nelson|Pierre-Charles Villeneuve|Decisive British victory|https://en.wikipedia.org/wiki/Battle_of_Trafalgar
Battle of Salamis|-480|37.952|23.568|Greco-Persian Wars|Naval|Decisive victory for the outnumbered Greek fleet, a turning point in the Persian Wars.|Greek city-states|Persian Empire|Themistocles|Xerxes I|Decisive Greek victory|https://en.wikipedia.org/wiki/Battle_of_Salamis
Battle of Midway|1942|28.208|-177.375|World War II|Naval|Turning point in the Pacific Theater of World War II.|United States|Empire of Japan|Frank J. Fletcher, Raymond A. Spruance|Chūichi Nagumo, Nobutake Kondō|Decisive American victory|https://en.wikipedia.org/wiki/Battle_of_Midway
Battle of Alesia|-52|47.53|4.49|Gallic Wars|Siege|Decisive Roman victory in the Gallic Wars, resulting in the Roman conquest of Gaul.|Roman Republic|Gallic Tribes|Julius Caesar|Vercingetorix|Decisive Roman victory|https://en.wikipedia.org/wiki/Battle_of_Alesia
Battle of Yorktown|1781|37.239|-76.510|American Revolutionary War|Siege|The last major battle of the American Revolutionary War.|United States, France|Great Britain|George Washington, Rochambeau|Lord Cornwallis|Decisive American-French victory|https://en.wikipedia.org/wiki/Siege_of_Yorktown
Battle of Gallipoli|1915|40.24|26.28|World War I|Amphibious Assault|A major Ottoman victory and a significant setback for the Allies.|Ottoman Empire|British Empire, France, Australia, New Zealand|Mustafa Kemal Atatürk|Ian Hamilton|Decisive Ottoman victory|https://en.wikipedia.org/wiki/Gallipoli_campaign
Siege of Jerusalem|1099|31.77|35.22|First Crusade|Siege|Crusaders captured the city from the Fatimid Caliphate.|Crusaders|Fatimid Caliphate|Godfrey of Bouillon|Iftikhar ad-Daula|Decisive Crusader victory|https://en.wikipedia.org/wiki/Siege_of_Jerusalem_(1099)
Siege of Baghdad|1258|33.34|44.40|Mongol Invasions|Siege|The fall of Baghdad marked the end of the Islamic Golden Age.|Mongol Empire|Abbasid Caliphate|Hulagu Khan|Al-Musta'sim|Decisive Mongol victory|https://en.wikipedia.org/wiki/Siege_of_Baghdad_(1258)
Battle of Red Cliffs|208|29.89|113.60|Three Kingdoms Period|Naval|Decisive victory for the allied forces of Sun Quan and Liu Bei against the numerically superior forces of Cao Cao.|Sun Quan, Liu Bei|Cao Cao|Zhou Yu, Cheng Pu|Cao Cao|Decisive allied victory|https://en.wikipedia.org/wiki/Battle_of_Red_Cliffs
Battle of Ayacucho|1824|-13.16|-74.22|Peruvian War of Independence|Pitched Battle|Decisive battle of the Peruvian War of Independence, securing the independence of Peru and much of South America.|Gran Colombia, Peru|Spanish Empire|Antonio José de Sucre|José de la Serna|Decisive Patriot victory|https://en.wikipedia.org/wiki/Battle_of_Ayacucho
Battle of Isandlwana|1879|-28.35|30.65|Anglo-Zulu War|Pitched Battle|The first major encounter in the Anglo-Zulu War and a decisive victory for the Zulus.|Zulu Kingdom|British Empire|Ntshingwayo kaMahole|Lord Chelmsford|Decisive Zulu victory|https://en.wikipedia.org/wiki/Battle_of_Isandlwana
Castle Hill Rebellion|1804|-33.74|150.96|Australian colonial history|Guerilla Action|A rebellion by Irish convicts in the British penal colony of New South Wales.|Irish convicts|British colonial forces|Phillip Cunningham|George Johnston|Decisive British victory|https://en.wikipedia.org/wiki/Castle_Hill_convict_rebellion
"""

# Read the string data into a pandas DataFrame, using '|' as the separator
df = pd.read_csv(io.StringIO(battle_data), sep='|')

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
        
        # Build the rich HTML for the popup, now with more compact styling
        popup_html = f"""
        <div style="width: 250px; font-size: 13px;">
            <h4 style="margin-bottom:5px; font-weight:bold; font-size: 14px;">{row['Battle']} ({row['Year']})</h4>
            <p style="margin:2px 0;"><strong>War:</strong> {row['War']}</p>
            <p style="margin:2px 0;"><strong>Type:</strong> {row['Battle_Type']}</p>
            <hr style="margin:5px 0;">
            <p style="margin:2px 0;"><em>{row['Description']}</em></p>
            <hr style="margin:5px 0;">
            <p style="margin:2px 0;"><strong>Belligerents:</strong><br>{row['Belligerents_A']} vs. {row['Belligerents_B']}</p>
            <p style="margin:2px 0;"><strong>Commanders:</strong><br>{row['Commanders_A']} vs. {row['Commanders_B']}</p>
            <p style="margin:2px 0;"><strong>Result:</strong> {row['Result']}</p>
            <a href="{row['Wiki_URL']}" target="_blank" rel="noopener noreferrer">Learn More on Wikipedia</a>
        </div>
        """
        
        # The tooltip on hover remains concise
        tooltip_text = f"{row['Battle']} ({row['Year']})"

        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_html, max_width=270), # Adjusted max_width
            tooltip=tooltip_text,
            icon=folium.Icon(color='darkred', icon=icon_name, prefix='fa')
        ).add_to(m)

# Display the map
st_data = st_folium(m, width=1200, height=800)
