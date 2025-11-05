from dash import Output, Input, html
import plotly.express as px
import pandas as pd
from data_helper import load_world_cup_data,country_to_iso2,get_flag_url, get_flag_url_by_iso


def register_callbacks(app, world_cup_overview_df: pd.DataFrame, matches_df: pd.DataFrame, players_df: pd.DataFrame):
    @app.callback(
        Output("world-cup-placements-graph", "figure"),
        Input('url', 'pathname'), # Use pathname as a trigger for initial load
    )
    def update_world_cup_placements_graph(pathname): # pathname receives the URL path, not directly used for data
        placement_data = []

        # Iterate through each World Cup year's overview data
        for index, row in world_cup_overview_df.iterrows():
            # Get placement information. Use .get() with default to handle potential missing columns
            # if the CSV has slight variations or missing data for certain years.
            winner = row.get('Winner')
            runner_up = row.get('Runners-Up')
            third = row.get('Third')
            fourth = row.get('Fourth')

            if pd.notna(winner):
                placement_data.append({'Country': winner, 'Placement': '1st Place'})
            if pd.notna(runner_up):
                placement_data.append({'Country': runner_up, 'Placement': '2nd Place'})
            if pd.notna(third):
                placement_data.append({'Country': third, 'Placement': '3rd Place'})
            if pd.notna(fourth):
                placement_data.append({'Country': fourth, 'Placement': '4th Place'})

        placement_df_processed = pd.DataFrame(placement_data)

        if placement_df_processed.empty:
            return px.bar(title="No World Cup placement data available.")

        # Count occurrences of each country for each placement
        aggregated_placements = placement_df_processed.groupby(['Country', 'Placement']).size().reset_index(name='Count')

        # To sort countries by total top-4 finishes in descending order
        country_total_finishes = aggregated_placements.groupby('Country')['Count'].sum().sort_values(ascending=False)
        sorted_countries = country_total_finishes.index.tolist()

        # Ensure consistent order of placements for color/grouping in the legend and bars
        placement_order = ['1st Place', '2nd Place', '3rd Place', '4th Place']
        # Convert 'Placement' to a categorical type with a specific order for consistent plotting
        aggregated_placements['Placement'] = pd.Categorical(aggregated_placements['Placement'], categories=placement_order, ordered=True)
        
        # Define custom colors for each placement for better visual distinction
        colors = {

            '1st Place': '#D4AF37', # Gold
            '2nd Place': '#D8D8D8', # Silver
            '3rd Place': '#B08D57', # Bronze
            '4th Place': '#4682B4'

        }

        fig = px.bar(
            aggregated_placements,
            x='Country',
            y='Count',
            color='Placement',
            category_orders={'Country': sorted_countries, 'Placement': placement_order}, # Apply sorting and category order
            title='FIFA World Cup Top 4 Placements by Country (1930-Present)',
            labels={'Count': 'Number of Placements', 'Country': 'Country', 'Placement': 'Placement'},
            height=600,
            barmode='stack',
            color_discrete_map=colors # Apply custom colors
        )
        
        fig.update_layout(xaxis_title="Country", yaxis_title="Number of Top-4 Finishes", 
                          legend_title_text="Placement", 
                          xaxis_tickangle=-45)
        fig.update_traces(marker_line_width=0)
        
        return fig
    # --- END MODIFIED CALLBACK ---

    # Callback for Match Goals Graph (e.g., goals per match over selected tournament)
    @app.callback(
        Output("match-goals-graph", "figure"),
        Input("matches-year-selector", "value"),
    )
    def update_match_goals_graph(selected_year):
        if selected_year is None:
            return px.line(title="Select a World Cup Year to see Match Goals")

        filtered_matches_df = matches_df[matches_df["Year"] == selected_year].copy()

        if filtered_matches_df.empty:
            return px.bar(title=f"No match data for World Cup {selected_year}")

        # Calculate total goals per match
        filtered_matches_df["Total Goals"] = filtered_matches_df["Home Team Goals"] + filtered_matches_df["Away Team Goals"]
        
        fig = px.bar(
            filtered_matches_df,
            x=filtered_matches_df.index,
            y="Total Goals",
            color="Stage",
            title=f"Total Goals per Match in FIFA World Cup {selected_year}",
            labels={"index": "Match Number"}
        )
        return fig


# Callback for Match Details Table with flags in team name columns
    @app.callback(
        Output("match-details-table-container", "children"),
        Input("matches-year-selector", "value"),
    )
    def update_match_details_table(selected_year):
        if selected_year is None:
            return html.P("Select a World Cup Year to see Match Details.")

        filtered_matches_df = matches_df[matches_df["Year"] == selected_year].copy()

        if filtered_matches_df.empty:
            return html.P(f"No match data for World Cup {selected_year}.")

        # Format the datetime column
        if 'Datetime' in filtered_matches_df.columns:
            filtered_matches_df['Datetime'] = pd.to_datetime(filtered_matches_df['Datetime'], errors='coerce')
            filtered_matches_df['Datetime'] = filtered_matches_df['Datetime'].dt.strftime('%d %b, %Y')

        # Columns to display
        display_cols = [
            "Datetime", "Stage", "Home Team Name", "Home Team Goals",
            "Away Team Goals", "Away Team Name", "Stadium", "City", "Win conditions"
        ]
        available_cols = [col for col in display_cols if col in filtered_matches_df.columns]
        table_df = filtered_matches_df[available_cols].fillna('N/A')

        # Table header
        table_header = [html.Thead(html.Tr([html.Th(col.replace('_', ' ')) for col in table_df.columns]))]

        # Build table body with flags and centered goals
        rows = []
        for i in range(len(table_df)):
            row = table_df.iloc[i].to_dict()
            cells = []

            for col in table_df.columns:
                cell_val = row.get(col, "")

                # Insert flags for team name columns
                if col in ["Home Team Name", "Home Team"]:
                    flag_url = get_flag_url(cell_val)
                    if flag_url:
                        cell_content = html.Div([
                            html.Img(src=flag_url, style={"height": "20px", "marginRight": "6px"}),
                            html.Span(cell_val)
                        ], style={"display": "flex", "alignItems": "center"})
                        cells.append(html.Td(cell_content))
                        continue
                elif col in ["Away Team Name", "Away Team"]:
                    flag_url = get_flag_url(cell_val)
                    if flag_url:
                        cell_content = html.Div([
                            html.Img(src=flag_url, style={"height": "20px", "marginRight": "6px"}),
                            html.Span(cell_val)
                        ], style={"display": "flex", "alignItems": "center"})
                        cells.append(html.Td(cell_content))
                        continue

                # Center the goals
                if col in ["Home Team Goals", "Away Team Goals"]:
                    cell_style = {"textAlign": "center", "width": "80px"}
                # Default style for datetime column
                elif col == "Datetime":
                    cell_style = {"whiteSpace": "nowrap", "width": "130px"}
                else:
                    cell_style = {}

                cells.append(html.Td(cell_val, style=cell_style))

            rows.append(html.Tr(cells))

        table_body = [html.Tbody(rows)]

        return html.Table(
            table_header + table_body,
            className="table table-striped table-hover",
            style={"width": "100%", "tableLayout": "auto"}
        )
