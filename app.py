import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import gspread
from google.oauth2.service_account import Credentials

# Set the page to wide mode
st.set_page_config(layout="wide")

st.title("BattleScape")

# --- Data Loading from Private Google Sheet ---

@st.cache_data(ttl=600) # Cache data for 10 minutes
def load_data_from_google_sheet(sheet_name="battlescape"):
    """
    Loads data from a private Google Sheet using service account credentials
    stored in Streamlit secrets.
    """
    try:
        creds_dict = st.secrets["gcp_service_account"]
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        spreadsheet = client.open(sheet_name)
        worksheet = spreadsheet.sheet1
        records = worksheet.get_all_records()
        df = pd.DataFrame(records)
        # Ensure numeric columns are the correct type
        df['Year'] = pd.to_numeric(df['Year'])
        df['Latitude'] = pd.to_numeric(df['Latitude'])
        df['Longitude'] = pd.to_numeric(df['Longitude'])
        return df
        
    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"⚠️ Google Sheet Error: Spreadsheet '{sheet_name}' not found. Please check the name and sharing settings.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"⚠️ An unexpected error occurred loading from Google Sheet: {e}")
        return pd.DataFrame()

df = load_data_from_google_sheet()

if df.empty:
    st.warning("Could not load battle data. Please ensure the Google Sheet is correctly set up and shared.")
    st.stop()

# --- Session State Initialization ---
if 'tour_active' not in st.session_state:
    st.session_state.tour_active = False
if 'tour_step' not in st.session_state:
    st.session_state.tour_step = 0
if 'selected_tour' not in st.session_state:
    st.session_state.selected_tour = "None"

# --- Sidebar UI ---
st.sidebar.header("Explore Battles")

# Guided Tour Selector
tour_options = ["None"] + sorted(df['War'].unique())
selected_tour = st.sidebar.selectbox(
    'Select a Guided Tour:', 
    tour_options, 
    index=tour_options.index(st.session_state.selected_tour)
)

# Update session state if tour selection changes
if selected_tour != st.session_state.selected_tour:
    st.session_state.selected_tour = selected_tour
    st.session_state.tour_active = (selected_tour != "None")
    st.session_state.tour_step = 0 # Reset step on new tour selection

st.sidebar.markdown("---")

# Standard Filters (disabled if a tour is active)
st.sidebar.header("Filter Battles")
is_tour_active = st.session_state.tour_active

war_list = ['All Wars'] + sorted(df['War'].unique())
selected_war = st.sidebar.selectbox(
    'Select a War:', 
    war_list, 
    disabled=is_tour_active
)

min_year = int(df['Year'].min())
max_year = int(df['Year'].max())
selected_years = st.sidebar.slider(
    'Select a Year Range:',
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    disabled=is_tour_active
)

# --- Data Filtering and Tour Logic ---
current_battle_id = None
if st.session_state.tour_active:
    # For a tour, the filtered data includes all battles of that war
    tour_df = df[df['War'] == st.session_state.selected_tour].sort_values(by='Year').reset_index(drop=True)
    filtered_df = tour_df
    
    st.sidebar.markdown("---")
    st.sidebar.header("Tour Controls")
    
    num_battles = len(tour_df)
    current_battle = tour_df.iloc[st.session_state.tour_step]
    current_battle_id = current_battle['Battle'] # Get the name of the current battle for highlighting
    
    st.sidebar.subheader(f"Step {st.session_state.tour_step + 1} of {num_battles}")
    st.sidebar.markdown(f"**{current_battle['Battle']} ({current_battle['Year']})**")
    st.sidebar.caption(current_battle['Description'])

    col1, col2 = st.sidebar.columns(2)
    if col1.button("Previous", use_container_width=True):
        if st.session_state.tour_step > 0:
            st.session_state.tour_step -= 1
            st.experimental_rerun()
    
    if col2.button("Next", use_container_width=True):
        if st.session_state.tour_step < num_battles - 1:
            st.session_state.tour_step += 1
            st.experimental_rerun()
            
else:
    # Standard Filter Logic
    if selected_war == 'All Wars':
        filtered_df = df
    else:
        filtered_df = df[df['War'] == selected_war]
    
    filtered_df = filtered_df[
        (filtered_df['Year'] >= selected_years[0]) & (filtered_df['Year'] <= selected_years[1])
    ]

# --- Map Creation ---
icon_map = {
    'Naval': 'anchor', 'Siege': 'university', 'Pitched Battle': 'shield-alt',
    'Guerilla Action': 'fire', 'Amphibious Assault': 'ship', 'Air Battle': 'plane'
}
default_icon = 'crosshairs'

if not filtered_df.empty:
    map_center = [filtered_df['Latitude'].mean(), filtered_df['Longitude'].mean()]
    zoom_start = 5 if len(filtered_df['War'].unique()) == 1 else 2
else:
    map_center = [20, 0]
    zoom_start = 2
    if not st.session_state.tour_active:
        st.warning("No battles found for the selected filters.")

m = folium.Map(location=map_center, zoom_start=zoom_start, tiles='CartoDB Positron')

if not filtered_df.empty:
    for index, row in filtered_df.iterrows():
        icon_name = icon_map.get(row['Battle_Type'], default_icon)
        
        # Determine icon color: green for current tour step, red for others
        icon_color = 'green' if row['Battle'] == current_battle_id else 'darkred'
        
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
        
        tooltip_text = f"{row['Battle']} ({row['Year']})"

        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_html, max_width=270),
            tooltip=tooltip_text,
            icon=folium.Icon(color=icon_color, icon=icon_name, prefix='fa')
        ).add_to(m)

# Use a key that changes only when the tour selection changes, for better stability
map_key = st.session_state.selected_tour
st_folium(m, key=map_key, width=1200, height=800)
