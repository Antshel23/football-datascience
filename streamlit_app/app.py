import streamlit as st
import pandas as pd
from scripts.radar_plot import plot_player 

# Set Streamlit to dark mode at the beginning
st.markdown(
    """
    <style>
    .reportview-container {
        background-color: #2b2b2b;
    }
    .sidebar .sidebar-content {
        background-color: #1a1a1a;
    }
    .sidebar .sidebar-title {
        color: #FFFFFF;
        font-size: 20px;
        padding: 10px;
    }
    .sidebar .sidebar-content .stSelectbox, .sidebar .sidebar-content .stButton {
        background-color: #333;
        color: #FFFFFF;
    }
    .sidebar .sidebar-content .stSelectbox:hover, .sidebar .sidebar-content .stButton:hover {
        background-color: #444;
    }
    .stHeader {
        color: #FFFFFF;
        font-size: 24px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load data
df = pd.read_csv('./data/maindata.csv') 

# Sidebar for user inputs
st.header("Football Player Pizza Plot")  
st.sidebar.header("Select Team and Player")  

# Get unique teams and timeframes from the dataframe
teams = df['Team within selected timeframe'].unique()
timeframes = df['Season'].unique()

# Add a select box for Team
selected_team = st.sidebar.selectbox('Select Team', teams)

# Filter players based on selected team
players_in_team = df[df['Team within selected timeframe'] == selected_team]['Player'].unique()
player_name = st.sidebar.selectbox('Select Player', players_in_team)

# Add select box for Season
season = st.sidebar.selectbox('Select Season', timeframes)

# Retrieve position based on player and season selection
position_row = df[(df['Player'] == player_name) & (df['Season'] == season)]
position = position_row['Position'].values[0] if not position_row.empty else None

# Plot the player
fig = plot_player(df, player_name, season, position, selected_team)  

# Display the plot or a message if no data
if fig is not None:
    st.pyplot(fig) 
else:
    st.write(f"No data available for {player_name} in {season}.")

