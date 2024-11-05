import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import PyPizza, FontManager
import numpy as np

def get_blue_shade(value):
    """Return a blue color that darkens with higher values (0-100)."""
    # Define light and dark blue with more contrast
    min_blue = np.array([173, 216, 230])  # RGB for light blue (LightSkyBlue)
    max_blue = np.array([0, 0, 139])      # RGB for dark blue (DarkBlue)

    # Interpolate color based on value (0-100)
    color = min_blue + (max_blue - min_blue) * (value / 100)
    return f"#{int(color[0]):02X}{int(color[1]):02X}{int(color[2]):02X}"


def plot_player(df, player_name, season, position, team):
    player_data = df[(df['Player'] == player_name) & (df['Season'] == season) & (df['Team within selected timeframe'] == team)]

    if player_data.empty:
        print("N/A: Player or season does not exist.")
        fig, ax = plt.subplots(figsize=(8, 8.5), subplot_kw=dict(polar=True))
        return fig

    # Define position-specific columns
    position_columns = {
        'CB': ["Defensive duels won, %", "Aerial duels won, %", "PAdj Interceptions", "Progressive runs per 90", "Successful dribbles per 90", 'Progressive passes per 90', 'Passes to final third per 90', 'Accurate progressive passes, %', 'Accurate passes to final third, %', 'Accurate long passes, %'],
        'FB': ["Defensive duels won, %", "Aerial duels won, %", "PAdj Interceptions", "Progressive runs per 90", "Successful dribbles per 90", 'Progressive passes per 90', 'Passes to final third per 90', 'Accurate progressive passes, %', 'Accurate passes to final third, %', 'Dangerous attacking actions per 90'],
        'CM': ["Successful defensive actions per 90", "Progressive runs per 90", "Successful dribbles per 90", 'Progressive passes per 90', 'Passes to final third per 90', 'Accurate progressive passes, %', 'Through passes per 90', 'xA per 90', 'xG per 90', 'Dangerous attacking actions per 90'],
        'WIDE': ["Successful defensive actions per 90", "Progressive runs per 90", "Successful dribbles per 90", 'Fouls suffered per 90', 'Passes to final third per 90', 'Key passes per 90', 'xA per 90', 'xA/shot assist', 'xG per 90', 'Dangerous attacking actions per 90'],
        'FW': ['Accurate short / medium passes, %', 'Passes to penalty area per 90', "Successful dribbles per 90", 'Deep completions per 90', 'Smart passes per 90', 'xA per 90', 'xA/shot assist', 'xG per 90', 'xG performance', 'Dangerous attacking actions per 90']
    }

    default_columns = [
        "Successful dribbles per 90", 'Progressive runs per 90', "xA/box entry", "xA per 90", 
        "Progressive passes per 90", "Accurate progressive passes, %", 
        "Passes to final third per 90", "Key passes per 90", "Through passes per 90",
        "xG per 90", "Aerial duels won, %", "Defensive duels won, %"
    ]

    # Select columns based on position, with a default if position is not found
    selected_columns = position_columns.get(position, default_columns)
    
    # Get values for selected columns
    values = player_data[selected_columns].values.flatten()

    # Ensure values are formatted as integers with no decimal places
    formatted_values = [int(round(v)) for v in values]

    # Check if lengths are equal
    if len(selected_columns) != len(formatted_values):
        print(f"Error: Length of params ({len(selected_columns)}) and values ({len(formatted_values)}) do not match for player {player_name} in season {season}.")
        return None  # or handle the error appropriately

    params = selected_columns

    # Generate slice colors based on value from light blue -> dark blue
    slice_colors = [get_blue_shade(value) for value in formatted_values]

    # Create figure and polar axes
    fig, ax = plt.subplots(figsize=(8, 8.5), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#0E1118")

    baker = PyPizza(
        params=params,
        background_color="#2b2b2b",
        straight_line_color="#2b2b2b",
        straight_line_lw=1,
        last_circle_lw=0,
        other_circle_lw=0,
        inner_circle_size=20
    )

    baker.make_pizza(
        formatted_values,
        ax=ax,
        color_blank_space="same",
        slice_colors=slice_colors,
        value_colors=["#FFFFFF"] * len(selected_columns),
        value_bck_colors=["#2b2b2b"] * len(selected_columns),
        blank_alpha=0.4,
        kwargs_slices=dict(edgecolor="#F2F2F2", zorder=2, linewidth=1),
        kwargs_params=dict(color="#FFFFFF", fontsize=8),
        kwargs_values=dict(color="#FFFFFF", fontsize=10, zorder=3, 
                           bbox=dict(edgecolor="#FFFFFF", facecolor="#2b2b2b", boxstyle="round,pad=0.2", lw=1))
    )

    fig.text(0.515, 0.965, player_name, size=16, ha="center", 
             fontproperties=FontManager('https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Regular.ttf').prop, color="#FFFFFF")
    fig.text(0.515, 0.923, season, size=13, ha="center", 
             fontproperties=FontManager('https://raw.githubusercontent.com/google/fonts/main/apache/robotoslab/RobotoSlab[wght].ttf').prop, color="#FFFFFF")

    return fig







