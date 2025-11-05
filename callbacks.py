from dash import Output, Input, html, State, no_update, callback_context
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from data_helper import get_flag_url


def register_callbacks(
    app,
    world_cup_overview_df: pd.DataFrame,
    matches_df: pd.DataFrame,
    players_df: pd.DataFrame,
):

    # --- CALLBACK 1 (No changes) ---
    @app.callback(
        Output("world-cup-overview-scatter", "figure"),
        Output("range-summary-output", "children"),
        Input("year-range-slider", "value")
    )
    def update_overview_scatter(year_range):
        df = world_cup_overview_df.copy()
        
        filtered_df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]
        summary_text = f"Highlighting {len(filtered_df)} tournaments from {year_range[0]} to {year_range[1]}, with a total of {filtered_df['GoalsScored'].sum():,} goals scored."
        df['Attendance'] = pd.to_numeric(df['Attendance'].str.replace('.', '', regex=False), errors='coerce')
        
        selected_df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]
        unselected_df = df[~((df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1]))]

        continent_color_map = {
            'Europe': '#1f77b4', 'South America': '#ff7f0e',
            'North America': '#2ca02c', 'Asia': '#d62728', 'Africa': '#9467bd'
        }

        fig = go.Figure()

        # --- LEGEND GENERATION HACK ---
        # Add a tiny, invisible scatter plot point for each continent.
        # This is ONLY to create the correct legend items.
        for continent, color in continent_color_map.items():
            fig.add_trace(go.Scatter(
                x=[None], y=[None], # No data
                mode='markers',
                marker=dict(color=color, size=10),
                name=continent, # This sets the legend text
                showlegend=True
            ))

        # --- DATA TRACES (with legend disabled) ---
        if not unselected_df.empty:
            fig.add_trace(go.Scatter(
                x=unselected_df['Year'], y=unselected_df['GoalsScored'], mode='markers',
                marker=dict(size=unselected_df['Attendance'] / 80000, color=unselected_df['Continent'].map(continent_color_map), opacity=0.3, line={'width': 1, 'color': 'DarkSlateGrey'}),
                customdata=unselected_df[['Year', 'Country', 'Winner', 'Attendance', 'Continent']],
                hovertemplate="<b>%{customdata[1]} %{x}</b><br>Winner: %{customdata[2]}<br>Continent: %{customdata[4]}<br>Goals: %{y}<br>Attendance: %{customdata[3]:,}<extra></extra>",
                showlegend=False # Disable legend for the data traces
            ))

        if not selected_df.empty:
            fig.add_trace(go.Scatter(
                x=selected_df['Year'], y=selected_df['GoalsScored'], mode='markers',
                marker=dict(size=selected_df['Attendance'] / 80000, color=selected_df['Continent'].map(continent_color_map), opacity=1.0, line={'width': 1.5, 'color': 'Black'}),
                customdata=selected_df[['Year', 'Country', 'Winner', 'Attendance', 'Continent']],
                hovertemplate="<b>%{customdata[1]} %{x}</b><br>Winner: %{customdata[2]}<br>Continent: %{customdata[4]}<br>Goals: %{y}<br>Attendance: %{customdata[3]:,}<extra></extra>",
                showlegend=False # Disable legend for the data traces
            ))
        
        # --- Layout and Styling ---
        fig.update_layout(
            title={'text': "<b>World Cup Tournaments Overview (1930-2014)</b>", 'y':0.95, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
            xaxis_title="Tournament Year",
            yaxis_title="Total Goals Scored",
            legend_title_text="<b>Host Continent</b>", # Make title bold
            showlegend=True, # Ensure the overall legend is visible
            margin=dict(l=40, r=40, t=60, b=40),
            transition_duration=300,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig, summary_text

    # --- CALLBACK 2 (RETURN STATEMENTS CORRECTED) ---
    @app.callback(
        Output("tournament-summary", "children"),
        Output("team-selector-dropdown", "options"),
        Output("team-selector-dropdown", "value"),
        Output("team-selector-dropdown", "disabled"),
        Output("team-player-summary", "children"),
        Output("clear-selection-button", "style"),
        Input("world-cup-overview-scatter", "clickData"),
        Input("team-selector-dropdown", "value"),
        Input("clear-selection-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def update_all_details_panels(clickData, selected_team, clear_clicks):
        triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]

        if triggered_id == "clear-selection-button":
            initial_summary = html.P(
                "Click on a tournament in the scatter plot to see details here.",
                style={"color": "#7f8c8d"},
            )
            initial_player_summary = html.P(
                "Select a team above to see their performance and player stats for the tournament.",
                style={"color": "#7f8c8d"},
            )
            hidden_button_style = {
                "float": "right",
                "display": "none",
                "marginBottom": "10px",
            }
            return (
                initial_summary,
                [],
                None,
                True,
                initial_player_summary,
                hidden_button_style,
            )

        visible_button_style = {
            "float": "right",
            "display": "block",
            "marginBottom": "10px",
        }

        if triggered_id == "world-cup-overview-scatter":
            if clickData is None:
                return no_update
            clicked_year = clickData["points"][0]["customdata"][0]
            tournament_info = world_cup_overview_df[
                world_cup_overview_df["Year"] == clicked_year
            ].iloc[0]

            def create_info_line(label, country_name):
                flag_url = get_flag_url(country_name)
                return html.P(
                    [
                        html.Strong(f"{label}: "),
                        html.Img(
                            src=flag_url,
                            style={
                                "height": "16px",
                                "marginRight": "5px",
                                "verticalAlign": "middle",
                            },
                        ),
                        country_name,
                    ],
                    style={"marginBottom": "5px"},
                )

            summary_children = html.Div(
                [
                    html.H4(
                        f"World Cup {tournament_info['Year']} in {tournament_info['Country']}",
                        style={"color": "#1a5276"},
                    ),
                    create_info_line("Winner", tournament_info["Winner"]),
                    create_info_line(
                        "Runner-Up", tournament_info["Runners-Up"]
                    ),
                    create_info_line("Third Place", tournament_info["Third"]),
                    html.Strong(
                        "Stats:",
                        style={"marginTop": "10px", "display": "block"},
                    ),
                    html.P(f"Goals Scored: {tournament_info['GoalsScored']}"),
                    html.P(
                        f"Matches Played: {tournament_info['MatchesPlayed']}"
                    ),
                    html.P(f"Attendance: {tournament_info['Attendance']}"),
                ]
            )
            year_matches = matches_df[matches_df["Year"] == clicked_year]
            all_teams = sorted(
                list(
                    set(year_matches["Home Team Name"].unique())
                    | set(year_matches["Away Team Name"].unique())
                )
            )
            team_options = [
                {"label": team, "value": team} for team in all_teams
            ]
            player_summary_reset = html.P(
                "Select a team above to see their performance.",
                style={"color": "#7f8c8d"},
            )
            return (
                summary_children,
                team_options,
                None,
                False,
                player_summary_reset,
                visible_button_style,
            )

        elif triggered_id == "team-selector-dropdown":
            if selected_team is None or clickData is None:
                # CORRECTED RETURN STATEMENT 1
                return (
                    no_update,
                    no_update,
                    None,
                    False,
                    html.P(
                        "Select a team above to see their performance.",
                        style={"color": "#7f8c8d"},
                    ),
                    visible_button_style,
                )

            selected_year = clickData["points"][0]["customdata"][0]

            team_matches = matches_df[
                (matches_df["Year"] == selected_year)
                & (
                    (matches_df["Home Team Name"] == selected_team)
                    | (matches_df["Away Team Name"] == selected_team)
                )
            ]
            match_table_header = [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("Stage"),
                            html.Th("Opponent"),
                            html.Th("Score"),
                            html.Th("Result"),
                        ]
                    )
                )
            ]
            match_table_rows = []
            for _, match in team_matches.iterrows():
                if match["Home Team Name"] == selected_team:
                    opponent, score = (
                        match["Away Team Name"],
                        f"{int(match['Home Team Goals'])} - {int(match['Away Team Goals'])}",
                    )
                else:
                    opponent, score = (
                        match["Home Team Name"],
                        f"{int(match['Away Team Goals'])} - {int(match['Home Team Goals'])}",
                    )
                if match["Home Team Goals"] == match["Away Team Goals"]:
                    result, badge_color = "D", "#6c757d"
                elif (
                    match["Home Team Name"] == selected_team
                    and match["Home Team Goals"] > match["Away Team Goals"]
                ) or (
                    match["Away Team Name"] == selected_team
                    and match["Away Team Goals"] > match["Home Team Goals"]
                ):
                    result, badge_color = "W", "#28a745"
                else:
                    result, badge_color = "L", "#dc3545"
                match_table_rows.append(
                    html.Tr(
                        [
                            html.Td(match["Stage"]),
                            html.Td(
                                [
                                    html.Img(
                                        src=get_flag_url(opponent),
                                        style={
                                            "height": "16px",
                                            "marginRight": "8px",
                                        },
                                    ),
                                    opponent,
                                ]
                            ),
                            html.Td(
                                score,
                                style={
                                    "fontWeight": "bold",
                                    "textAlign": "center",
                                },
                            ),
                            html.Td(
                                html.Span(
                                    result,
                                    style={
                                        "backgroundColor": badge_color,
                                        "color": "white",
                                        "padding": "3px 10px",
                                        "borderRadius": "6px",
                                        "fontWeight": "bold",
                                        "fontSize": "12px",
                                    },
                                )
                            ),
                        ]
                    )
                )
            match_journey_table = html.Table(
                match_table_header + [html.Tbody(match_table_rows)],
                className="table table-sm mt-2",
            )

            team_match_ids = team_matches["MatchID"].unique()
            team_initials = (
                team_matches["Home Team Initials"].iloc[0]
                if selected_team == team_matches["Home Team Name"].iloc[0]
                else team_matches["Away Team Initials"].iloc[0]
            )
            team_players_events = players_df[
                (players_df["MatchID"].isin(team_match_ids))
                & (players_df["Team Initials"] == team_initials)
            ]
            player_roster = sorted(team_players_events["Player Name"].unique())

            player_stats = []
            for player in player_roster:
                player_events = team_players_events[
                    team_players_events["Player Name"] == player
                ]
                goals = (
                    player_events["Event"].str.contains("G", na=False).sum()
                )
                yellow_cards = (
                    player_events["Event"].str.contains("Y", na=False).sum()
                )
                red_cards = (
                    player_events["Event"].str.contains("R", na=False).sum()
                )
                player_stats.append(
                    {
                        "Player": player,
                        "Goals": goals,
                        "Yellow Cards": yellow_cards,
                        "Red Cards": red_cards,
                    }
                )

            if player_stats:
                stats_df = pd.DataFrame(player_stats)
                stats_df = stats_df.sort_values(
                    by=["Goals", "Player"], ascending=[False, True]
                )
                player_table_header = [
                    html.Thead(
                        html.Tr(
                            [
                                html.Th("Player"),
                                html.Th("Goals ⚽️"),
                                html.Th("Yellow Cards"),
                                html.Th("Red Cards"),
                            ]
                        )
                    )
                ]
                player_table_rows = []
                for i in range(len(stats_df)):
                    row = stats_df.iloc[i]
                    player_table_rows.append(
                        html.Tr(
                            [
                                html.Td(row["Player"]),
                                html.Td(
                                    "⚽️" * row["Goals"]
                                    if row["Goals"] > 0
                                    else "0"
                                ),
                                html.Td(
                                    "🟨" * row["Yellow Cards"]
                                    if row["Yellow Cards"] > 0
                                    else "0"
                                ),
                                html.Td(
                                    "🟥" * row["Red Cards"]
                                    if row["Red Cards"] > 0
                                    else "0"
                                ),
                            ]
                        )
                    )
                player_table = html.Table(
                    player_table_header + [html.Tbody(player_table_rows)],
                    className="table table-sm table-striped mt-3",
                )
            else:
                player_table = html.P(
                    "No player data available for this team in this tournament."
                )

            team_flag_url = get_flag_url(selected_team)
            team_player_summary_children = html.Div(
                [
                    html.H5(
                        [
                            html.Img(
                                src=team_flag_url,
                                style={
                                    "height": "24px",
                                    "marginRight": "8px",
                                    "verticalAlign": "middle",
                                },
                            ),
                            f"{selected_team}'s Journey in {selected_year}",
                        ],
                        style={"color": "#1a5276"},
                    ),
                    html.H6("Match Results", style={"marginTop": "15px"}),
                    match_journey_table,
                    html.H6("Player Statistics", style={"marginTop": "20px"}),
                    player_table,
                ]
            )

            # CORRECTED RETURN STATEMENT 2
            return (
                no_update,
                no_update,
                selected_team,
                False,
                team_player_summary_children,
                visible_button_style,
            )

        return no_update
