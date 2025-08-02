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
        # Load Google Cloud Platform service account credentials from Streamlit secrets.
        creds_dict = st.secrets["gcp_service_account"]
        
        # Define the scopes required for Google Sheets and Drive APIs.
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        
        # Open the spreadsheet and select the first sheet.
        spreadsheet = client.open(sheet_name)
        worksheet = spreadsheet.sheet1
        
        # Get all records from the sheet and convert to a pandas DataFrame.
        records = worksheet.get_all_records()
        df = pd.DataFrame(records)
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
    st.stop() # Stop the app if data loading fails

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
        
        # Build the rich HTML for the popup
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
            popup=folium.Popup(popup_html, max_width=270),
            tooltip=tooltip_text,
            icon=folium.Icon(color='darkred', icon=icon_name, prefix='fa')
        ).add_to(m)

# Display the map
st_data = st_folium(m, width=1200, height=800)
