from dash import Dash, dcc, html
import pandas as pd
from layout import get_layout
from callbacks import register_callbacks
from data_helper import load_world_cup_data, add_continent_column 

# load data
print("--- App Startup: Loading FIFA World Cup Data from local CSVs ---")
world_cup_overview_df, matches_df, players_df = load_world_cup_data()

if world_cup_overview_df is not None:
    world_cup_overview_df = add_continent_column(world_cup_overview_df)

# Basic error handling for data loading
if world_cup_overview_df is None or matches_df is None or players_df is None:
    print("FATAL ERROR: Failed to load all World Cup data from CSVs. Please check if files exist and are correctly formatted.")
    # Initialize empty DataFrames to prevent further errors if data loading failed
    world_cup_overview_df = pd.DataFrame(columns=['Year', 'Host', 'Winner', 'Runners-Up', 'Third', 'Fourth', 'Goals Scored', 'Qualified Teams', 'Matches Played', 'Attendance'])
    matches_df = pd.DataFrame(columns=['Year', 'Datetime', 'Stage', 'Stadium', 'City', 'Home Team Name', 'Away Team Name', 'Home Team Goals', 'Away Team Goals', 'Win conditions', 'Attendance', 'Half-time Home Goals', 'Half-time Away Goals', 'Referee', 'Assistant 1', 'Assistant 2', 'Round', 'MatchID', 'Home Team Initials', 'Away Team Initials'])
    players_df = pd.DataFrame(columns=['RoundID', 'MatchID', 'Team Initials', 'Player Name', 'Event'])


app = Dash(__name__)

# Add dcc.Location to the layout to enable 'Input('url', 'pathname')' callback trigger
app.layout = html.Div([
    dcc.Location(id='url', refresh=False), # This component is crucial for the 'pathname' Input
    get_layout(world_cup_overview_df) 
])
# app.layout = get_layout(world_cup_overview_df)


register_callbacks(app, world_cup_overview_df, matches_df, players_df)

if __name__ == "__main__":
    app.run(debug=True)

    