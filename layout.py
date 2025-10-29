from dash import html, dcc
import pandas as pd

def get_layout(world_cup_overview_df: pd.DataFrame):    
    years = world_cup_overview_df["Year"].dropna().astype(int).sort_values(ascending=False).unique()
    year_options = [{"label": str(year), "value": year} for year in years]

    return html.Div(children=[
        html.H1(children="FIFA World Cup Data Analysis", style={"textAlign": "center", "color": "#005a30"}), # FIFA green

        html.Div([
            html.H3("World Cup Top 4 Placements by Country", style={'textAlign': 'center'}),
            html.P("This graph shows how many times each country has finished 1st, 2nd, 3rd, or 4th in the World Cup, sorted by total top-4 finishes.", 
                   style={'textAlign': 'center', 'marginBottom': '20px'}),
            dcc.Graph(id="world-cup-placements-graph"),
        ], style={"border": "1px solid #ddd", "padding": "10px", "margin": "10px", "borderRadius": "5px"}),

        html.Div([
            html.H3("Tournament Match Details", style={'textAlign': 'center'}),
            dcc.Dropdown(
                id="matches-year-selector",
                options=year_options,
                value=years[0] if len(years) > 0 else None, # Default to latest year if available
                placeholder="Select a World Cup Year for Match Details",
                style={"width": "50%", "margin": "10px auto"}
            ),
            dcc.Graph(id="match-goals-graph"),
            html.H4("Match Results Table", style={'textAlign': 'center', 'marginTop': '20px'}),
            html.Div(id="match-details-table-container", style={"maxHeight": "400px", "overflowY": "scroll"})

        ], style={"border": "1px solid #ddd", "padding": "10px", "margin": "10px", "borderRadius": "5px"}),
    ])