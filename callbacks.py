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

        # --- LEGEND GENERATION  ---
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

    # --- REWORKED CALLBACK 2: Handles clicks on the scatter plot to update details and Golden Boot ---
    @app.callback(
        Output("tournament-summary", "children"),
        Output("golden-boot-tracker", "children"),
        Output("red-card-tracker", "children"), # New output
        Output("team-selector-dropdown", "options"),
        Output("team-selector-dropdown", "value"),
        Output("team-selector-dropdown", "disabled"),
        Output("clear-selection-button", "style"),
        Input("world-cup-overview-scatter", "clickData"),
        Input("clear-selection-button", "n_clicks")
    )
    def update_tournament_details(clickData, clear_clicks):
        ctx = callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # --- Helper function to create leaderboard tables ---
        def create_leaderboard_table(df, metric_col, title):
            if df.empty:
                return html.P(f"No {metric_col.lower()} recorded.", style={"color":"#7f8c8d"})
            
            header = html.Thead(html.Tr([html.Th("Player"), html.Th("Team"), html.Th(metric_col)]))
            rows = [html.Tr([html.Td(row['Player Name']), html.Td(row['Team Initials']), html.Td(row[metric_col], style={'fontWeight': 'bold'})]) for i, row in df.iterrows()]
            return html.Table([header, html.Tbody(rows)], className="table table-sm table-striped mt-3")

        # --- DEFAULT STATE (No tournament selected or cleared) ---
        if triggered_id == "clear-selection-button" or clickData is None:
            
            # All-Time Golden Boot
            all_goals = players_df[players_df['Event'].str.contains('G', na=False)]
            all_top_scorers = all_goals.groupby(['Player Name', 'Team Initials'])['Event'].count().reset_index().rename(columns={'Event': 'Goals'})
            all_top_scorers = all_top_scorers.sort_values(by=['Goals', 'Player Name'], ascending=[False, True]).head(10)
            all_time_boot_table = create_leaderboard_table(all_top_scorers, 'Goals', 'All-Time Top Scorers')

            # All-Time Red Cards
            all_reds = players_df[players_df['Event'].str.contains('R', na=False)]
            all_top_reds = all_reds.groupby(['Player Name', 'Team Initials'])['Event'].count().reset_index().rename(columns={'Event': 'Red Cards'})
            all_top_reds = all_top_reds.sort_values(by=['Red Cards', 'Player Name'], ascending=[False, True]).head(10)
            all_time_red_table = create_leaderboard_table(all_top_reds, 'Red Cards', 'All-Time Red Cards')

            initial_summary = html.P("Click on a tournament to see details.", style={"color":"#7f8c8d"})
            return initial_summary, all_time_boot_table, all_time_red_table, [], None, True, {'display': 'none'}

        # --- TOURNAMENT SELECTED STATE ---
        clicked_year = clickData["points"][0]["customdata"][0]
        tournament_info = world_cup_overview_df[world_cup_overview_df["Year"] == clicked_year].iloc[0]

        # --- Tournament Summary Panel ---
        def create_info_line(label, country_name):
            flag_url = get_flag_url(country_name)
            return html.P([html.Strong(f"{label}: "), html.Img(src=flag_url, style={"height": "16px", "marginRight": "5px", "verticalAlign": "middle"}), country_name], style={"marginBottom": "5px"})

        summary_children = html.Div([
            html.H4(f"World Cup {tournament_info['Year']} in {tournament_info['Country']}", style={"color": "#1a5276"}),
            create_info_line("Winner", tournament_info["Winner"]),
            create_info_line("Runner-Up", tournament_info["Runners-Up"]),
            create_info_line("Third Place", tournament_info["Third"]),
            html.Strong("Stats:", style={"marginTop": "10px", "display": "block"}),
            html.P(f"Goals Scored: {tournament_info['GoalsScored']}"),
            html.P(f"Matches Played: {tournament_info['MatchesPlayed']}"),
            html.P(f"Attendance: {tournament_info['Attendance']}"),
        ])

        # --- Filter players data for the selected tournament ---
        year_matches_ids = matches_df[matches_df['Year'] == clicked_year]['MatchID'].unique()
        tournament_players = players_df[players_df['MatchID'].isin(year_matches_ids)]

        # Tournament Golden Boot
        goals = tournament_players[tournament_players['Event'].str.contains('G|P', na=False)]
        top_scorers = goals.groupby(['Player Name', 'Team Initials'])['Event'].count().reset_index().rename(columns={'Event': 'Goals'})
        top_scorers = top_scorers.sort_values(by=['Goals', 'Player Name'], ascending=[False, True]).head(10)
        tournament_boot_table = create_leaderboard_table(top_scorers, 'Goals', f'{clicked_year} Top Scorers')

        # Tournament Red Cards
        reds = tournament_players[tournament_players['Event'].str.contains('R', na=False)]
        top_reds = reds.groupby(['Player Name', 'Team Initials'])['Event'].count().reset_index().rename(columns={'Event': 'Red Cards'})
        top_reds = top_reds.sort_values(by=['Red Cards', 'Player Name'], ascending=[False, True]).head(10)
        tournament_red_table = create_leaderboard_table(top_reds, 'Red Cards', f'{clicked_year} Red Cards')

        # --- Team Selector Population ---
        year_matches = matches_df[matches_df["Year"] == clicked_year]
        all_teams = sorted(list(set(year_matches["Home Team Name"].unique()) | set(year_matches["Away Team Name"].unique())))
        team_options = [{"label": team, "value": team} for team in all_teams]

        return summary_children, tournament_boot_table, tournament_red_table, team_options, None, False, {'float': 'right', 'display': 'block', 'marginBottom': '10px'}

    # --- REWORKED CALLBACK 3: Handles team selection to update journey and H2H ---
    @app.callback(
        Output("team-player-summary", "children"),
        Output("opponent-selector-dropdown", "options"),
        Output("opponent-selector-dropdown", "value"),
        Output("opponent-selector-dropdown", "disabled"),
        Output("h2h-section", "style"),
        Output("h2h-separator", "style"),
        Input("team-selector-dropdown", "value"),
        State("world-cup-overview-scatter", "clickData"), # Use State to get the year without triggering callback
        prevent_initial_call=True
    )
    def update_team_details(selected_team, clickData):
        initial_summary = html.P("Select a team to see their performance.", style={"color":"#7f8c8d"})
        
        if selected_team is None or clickData is None:
            return initial_summary, [], None, True, {'display': 'none'}, {'display': 'none'}

        selected_year = clickData["points"][0]["customdata"][0]
        
        # --- Team Journey & Player Stats ---
        team_matches = matches_df[(matches_df["Year"] == selected_year) & ((matches_df["Home Team Name"] == selected_team) | (matches_df["Away Team Name"] == selected_team))]
        
        match_table_rows = []
        for _, match in team_matches.iterrows():
            is_home_team = match["Home Team Name"] == selected_team
            opponent = match["Away Team Name"] if is_home_team else match["Home Team Name"]
            score = f"{int(match['Home Team Goals'])} - {int(match['Away Team Goals'])}" if is_home_team else f"{int(match['Away Team Goals'])} - {int(match['Home Team Goals'])}"
            
            if match["Home Team Goals"] == match["Away Team Goals"]: result, color = "D", "#6c757d"
            elif (is_home_team and match["Home Team Goals"] > match["Away Team Goals"]) or (not is_home_team and match["Away Team Goals"] > match["Home Team Goals"]): result, color = "W", "#28a745"
            else: result, color = "L", "#dc3545"

            match_table_rows.append(html.Tr([
                html.Td(match["Stage"]),
                html.Td([html.Img(src=get_flag_url(opponent), style={"height": "16px", "marginRight": "8px"}), opponent]),
                html.Td(score, style={"fontWeight": "bold", "textAlign": "center"}),
                html.Td(html.Span(result, style={"backgroundColor": color, "color": "white", "padding": "3px 10px", "borderRadius": "6px", "fontWeight": "bold", "fontSize": "12px"}))
            ]))
        
        match_table_header = html.Thead(html.Tr([html.Th("Stage"), html.Th("Opponent"), html.Th("Score"), html.Th("Result")]))
        match_journey_table = html.Table([match_table_header, html.Tbody(match_table_rows)], className="table table-sm mt-2")

        # --- Player Stats ---
        team_match_ids = team_matches["MatchID"].unique()
        team_initials = team_matches[team_matches['Home Team Name'] == selected_team]['Home Team Initials'].iloc[0] if selected_team in team_matches['Home Team Name'].values else team_matches[team_matches['Away Team Name'] == selected_team]['Away Team Initials'].iloc[0]
        
        team_players_events = players_df[(players_df["MatchID"].isin(team_match_ids)) & (players_df["Team Initials"] == team_initials)]
        player_roster = sorted(team_players_events["Player Name"].unique())
        
        player_stats = []
        for player in player_roster:
            player_events = team_players_events[team_players_events["Player Name"] == player]
            player_stats.append({
                "Player": player,
                "Goals": player_events["Event"].str.contains("G|P", na=False).sum(),
                "Yellow Cards": player_events["Event"].str.contains("Y", na=False).sum(),
                "Red Cards": player_events["Event"].str.contains("R", na=False).sum(),
            })
        
        stats_df = pd.DataFrame(player_stats).sort_values(by=["Goals", "Player"], ascending=[False, True])
        player_table_header = html.Thead(html.Tr([html.Th("Player"), html.Th("Goals ⚽️"), html.Th("Yellow"), html.Th("Red")]))
        player_table_rows = [html.Tr([html.Td(row["Player"]), html.Td(row["Goals"]), html.Td(row["Yellow Cards"]), html.Td(row["Red Cards"])]) for i, row in stats_df.iterrows()]
        player_table = html.Table([player_table_header, html.Tbody(player_table_rows)], className="table table-sm table-striped mt-3")
        
        team_player_summary = html.Div([
            html.H5([html.Img(src=get_flag_url(selected_team), style={"height": "24px", "marginRight": "8px", "verticalAlign": "middle"}), f"{selected_team}'s Journey in {selected_year}"], style={"color": "#1a5276"}),
            html.H6("Match Results", style={"marginTop": "15px"}), match_journey_table,
            html.H6("Player Statistics", style={"marginTop": "20px"}), player_table,
        ])

        # --- Opponent Dropdown for H2H ---
        opponents = sorted(pd.concat([team_matches[team_matches['Home Team Name'] != selected_team]['Home Team Name'], team_matches[team_matches['Away Team Name'] != selected_team]['Away Team Name']]).unique())
        opponent_options = [{'label': opp, 'value': opp} for opp in opponents]

        return team_player_summary, opponent_options, None, False, {'display': 'block'}, {'display': 'block'}

    # --- REWORKED CALLBACK 4: H2H Analysis (mostly the same, just cleaner) ---
    @app.callback(
        Output("h2h-analysis-output", "children"),
        Input("opponent-selector-dropdown", "value"),
        State("team-selector-dropdown", "value"),
        prevent_initial_call=True
    )
    def update_h2h_analysis(opponent, team1):
        if not opponent or not team1:
            return None

        h2h_matches = matches_df[((matches_df['Home Team Name'] == team1) & (matches_df['Away Team Name'] == opponent)) | ((matches_df['Home Team Name'] == opponent) & (matches_df['Away Team Name'] == team1))]

        if h2h_matches.empty:
            return html.P("No all-time World Cup matches found between these teams.")

        team1_wins = ((h2h_matches['Home Team Name'] == team1) & (h2h_matches['Home Team Goals'] > h2h_matches['Away Team Goals'])).sum() + \
                     ((h2h_matches['Away Team Name'] == team1) & (h2h_matches['Away Team Goals'] > h2h_matches['Home Team Goals'])).sum()
        opponent_wins = len(h2h_matches) - team1_wins - (h2h_matches['Home Team Goals'] == h2h_matches['Away Team Goals']).sum()
        draws = (h2h_matches['Home Team Goals'] == h2h_matches['Away Team Goals']).sum()
        
        summary_text = f"Matches: {len(h2h_matches)} | {team1} Wins: {team1_wins} | {opponent} Wins: {opponent_wins} | Draws: {draws}"
        
        team1_goals = h2h_matches.loc[h2h_matches['Home Team Name'] == team1, 'Home Team Goals'].sum() + h2h_matches.loc[h2h_matches['Away Team Name'] == team1, 'Away Team Goals'].sum()
        opponent_goals = h2h_matches.loc[h2h_matches['Home Team Name'] == opponent, 'Home Team Goals'].sum() + h2h_matches.loc[h2h_matches['Away Team Name'] == opponent, 'Away Team Goals'].sum()

        fig = go.Figure([
            go.Bar(name=team1, x=['Goals Scored'], y=[team1_goals], marker_color='#1f77b4'),
            go.Bar(name=opponent, x=['Goals Scored'], y=[opponent_goals], marker_color='#ff7f0e')
        ])
        fig.update_layout(barmode='group', title=f"All-Time Goals: {team1} vs {opponent}", margin=dict(l=20, r=20, t=40, b=20), height=250)

        return html.Div([html.H5(f"All-Time Record: {team1} vs. {opponent}", style={"fontWeight":"bold"}), html.P(summary_text), dcc.Graph(figure=fig)])
