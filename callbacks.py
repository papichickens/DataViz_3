from dash import Output, Input, html, State, no_update, callback_context, dcc
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from data_helper import get_flag_url

def create_leaderboard_table(df, metric_col):
    """Creates a Dash HTML table for a leaderboard."""
    if df.empty:
        return html.P(f"No {metric_col.lower()} recorded.", style={"color":"#7f8c8d"})
    
    header = html.Thead(html.Tr([html.Th("Player"), html.Th("Team"), html.Th(metric_col)]))
    rows = [html.Tr([html.Td(row['Player Name']), html.Td(row['Team Initials']), html.Td(row[metric_col], style={'fontWeight': 'bold'})]) for _, row in df.iterrows()]
    return html.Table([header, html.Tbody(rows)], className="table table-sm table-striped mt-3")

def create_map_figure(all_teams_list, iso_map, teams_to_highlight=None, winner=None, runner_up=None, third_place=None):
    """
    Creates a Plotly Express choropleth map figure with a consolidated status
    for countries with multiple teams (like the UK).
    """
    all_teams_df = pd.DataFrame(all_teams_list, columns=['country'])
    all_teams_df['iso_alpha'] = all_teams_df['country'].map(iso_map)
    all_teams_df['status'] = 'Participated Historically'
    
    # Assign statuses as before
    if teams_to_highlight:
        all_teams_df.loc[all_teams_df['country'].isin(teams_to_highlight), 'status'] = 'Active Participant'
    if third_place:
        all_teams_df.loc[all_teams_df['country'] == third_place, 'status'] = 'Third Place'
    if runner_up:
        all_teams_df.loc[all_teams_df['country'] == runner_up, 'status'] = 'Runner-Up'
    if winner:
        all_teams_df.loc[all_teams_df['country'] == winner, 'status'] = 'Winner'

    # --- NEW CONSOLIDATION LOGIC TO FIX THE UK BUG ---
    # 1. Define the order of importance for each status.
    status_order = [
        'Participated Historically', 
        'Active Participant', 
        'Third Place', 
        'Runner-Up', 
        'Winner'
    ]
    # 2. Convert the 'status' column to an ordered Categorical data type.
    # This teaches pandas the hierarchy of our statuses.
    all_teams_df['status'] = pd.Categorical(all_teams_df['status'], categories=status_order, ordered=True)

    # 3. Sort the DataFrame first by ISO code, then by the ranked status.
    # This brings the most important status for each country to the end of its group.
    all_teams_df = all_teams_df.sort_values(by=['iso_alpha', 'status'])

    # 4. Drop duplicate ISO codes, keeping only the LAST one.
    # Because we sorted, the 'last' one is guaranteed to be the highest-ranking status.
    map_df = all_teams_df.drop_duplicates(subset='iso_alpha', keep='last')
    # --- END OF NEW LOGIC ---

    fig = px.choropleth(
        map_df,  # Use the new, cleaned DataFrame for plotting
        locations="iso_alpha",
        color="status",
        hover_name="country",
        color_discrete_map={
            'Participated Historically': '#d4e6f1',
            'Active Participant': '#2e86c1',
            'Winner': 'gold',
            'Runner-Up': 'silver',
            'Third Place': '#cd7f32'
        },
        category_orders={"status": ["Winner", "Runner-Up", "Third Place", "Active Participant", "Participated Historically"]},
        projection="natural earth"
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        geo=dict(showframe=False, showcoastlines=False),
        legend=dict(
            title_text='Status',
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5,
            font=dict(size=8),
            title_font=dict(size=12)
        )
    )
    return fig

def register_callbacks(
    app,
    world_cup_overview_df: pd.DataFrame,
    matches_df: pd.DataFrame,
    players_df: pd.DataFrame,
    all_teams: list,
    country_iso_map: dict
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

    @app.callback(
        Output("world-map-choropleth", "figure"),
        Output("tournament-summary", "children"),
        Output("golden-boot-tracker", "children"),
        # Output("red-card-tracker", "children"),
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

        if triggered_id == "clear-selection-button" or clickData is None:
            map_fig = create_map_figure(all_teams, country_iso_map)
            
            all_goals = players_df[players_df['Event'].str.contains('G|P', na=False)]
            all_top_scorers = all_goals.groupby(['Player Name', 'Team Initials'])['Event'].count().reset_index().rename(columns={'Event': 'Goals'}).sort_values(by='Goals', ascending=False).head(10)
            all_time_boot_table = create_leaderboard_table(all_top_scorers, 'Goals')
        

            initial_summary = html.P("Click on a tournament to see details.", style={"color":"#7f8c8d"})
            return map_fig, initial_summary, all_time_boot_table, [], None, True, {'display': 'none'}

        # --- TOURNAMENT SELECTED STATE ---
        clicked_year = clickData["points"][0]["customdata"][0]
        
        year_matches = matches_df[matches_df["Year"] == clicked_year]
        tournament_teams = sorted(list(set(year_matches["Home Team Name"].unique()) | set(year_matches["Away Team Name"].unique())))
        tournament_info = world_cup_overview_df[world_cup_overview_df["Year"] == clicked_year].iloc[0]
        
        map_fig = create_map_figure(
            all_teams_list=all_teams,
            iso_map=country_iso_map,
            teams_to_highlight=tournament_teams,
            winner=tournament_info['Winner'],
            runner_up=tournament_info['Runners-Up'],
            third_place=tournament_info['Third']
        )
        
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
        
        year_matches_ids = matches_df[matches_df['Year'] == clicked_year]['MatchID'].unique()
        tournament_players = players_df[players_df['MatchID'].isin(year_matches_ids)]
        goals = tournament_players[tournament_players['Event'].str.contains('G|P', na=False)]
        top_scorers = goals.groupby(['Player Name', 'Team Initials'])['Event'].count().reset_index().rename(columns={'Event': 'Goals'}).sort_values(by=['Goals', 'Player Name'], ascending=[False, True]).head(10)
        tournament_boot_table = create_leaderboard_table(top_scorers, 'Goals')
        
        # CORRECT: Use the unique 'tournament_teams' variable to populate the dropdown
        team_options = [{"label": team, "value": team} for team in tournament_teams]

        return map_fig, summary_children, tournament_boot_table, team_options, None, False, {'float': 'right', 'display': 'block', 'marginBottom': '10px'}

    # --- REWORKED CALLBACK 3: Handles team selection to update journey and H2H ---
    @app.callback(
        Output("team-player-summary", "children"),
        Output("opponent-selector-dropdown", "options"),
        Output("opponent-selector-dropdown", "value"),
        Output("opponent-selector-dropdown", "disabled"),
        # MODIFIED: Target the new parent panel's style
        Output("h2h-panel", "style"),
        # REMOVED: No longer need to target the old children
        # Output("h2h-section", "style"),
        # Output("h2h-separator", "style"),
        Input("team-selector-dropdown", "value"),
        State("world-cup-overview-scatter", "clickData"),
        prevent_initial_call=True
    )
    def update_team_details(selected_team, clickData):
        initial_summary = html.P("Select a team to see their performance.", style={"color":"#7f8c8d"})
        
        # When no team is selected, hide the H2H panel
        if selected_team is None or clickData is None:
            # MODIFIED: Return style for the parent panel
            return initial_summary, [], None, True, {'display': 'none'}

        selected_year = clickData["points"][0]["customdata"][0]
        
        # --- Team Journey & Player Stats (This logic is unchanged) ---
        team_matches = matches_df[(matches_df["Year"] == selected_year) & ((matches_df["Home Team Name"] == selected_team) | (matches_df["Away Team Name"] == selected_team))]
        
        match_table_rows = []
        for _, match in team_matches.iterrows():
            is_home_team = match["Home Team Name"] == selected_team
            opponent = match["Away Team Name"] if is_home_team else match["Home Team Name"]
            score = f"{int(match['Home Team Goals'])} - {int(match['Away Team Goals'])}" if is_home_team else f"{int(match['Away Team Goals'])} - {int(match['Home Team Goals'])}"
            if match["Home Team Goals"] == match["Away Team Goals"]: result, color = "D", "#6c757d"
            elif (is_home_team and match["Home Team Goals"] > match["Away Team Goals"]) or (not is_home_team and match["Away Team Goals"] > match["Home Team Goals"]): result, color = "W", "#28a745"
            else: result, color = "L", "#dc3545"
            match_table_rows.append(html.Tr([html.Td(match["Stage"]),html.Td([html.Img(src=get_flag_url(opponent), style={"height": "16px", "marginRight": "8px"}), opponent]),html.Td(score, style={"fontWeight": "bold", "textAlign": "center"}),html.Td(html.Span(result, style={"backgroundColor": color, "color": "white", "padding": "3px 10px", "borderRadius": "6px", "fontWeight": "bold", "fontSize": "12px"}))]))
        match_table_header = html.Thead(html.Tr([html.Th("Stage"), html.Th("Opponent"), html.Th("Score"), html.Th("Result")]))
        match_journey_table = html.Table([match_table_header, html.Tbody(match_table_rows)], className="table table-sm mt-2")
        
        team_match_ids = team_matches["MatchID"].unique()
        team_initials = team_matches[team_matches['Home Team Name'] == selected_team]['Home Team Initials'].iloc[0] if selected_team in team_matches['Home Team Name'].values else team_matches[team_matches['Away Team Name'] == selected_team]['Away Team Initials'].iloc[0]
        team_players_events = players_df[(players_df["MatchID"].isin(team_match_ids)) & (players_df["Team Initials"] == team_initials)]
        player_roster = sorted(team_players_events["Player Name"].unique())
        player_stats = []
        for player in player_roster:
            player_events = team_players_events[team_players_events["Player Name"] == player]
            player_stats.append({"Player": player,"Goals": player_events["Event"].str.contains("G|P", na=False).sum(),"Yellow Cards": player_events["Event"].str.contains("Y", na=False).sum(),"Red Cards": player_events["Event"].str.contains("R", na=False).sum()})
        stats_df = pd.DataFrame(player_stats).sort_values(by=["Goals", "Player"], ascending=[False, True])
        player_table_header = html.Thead(html.Tr([html.Th("Player"), html.Th("Goals"), html.Th("Yellow"), html.Th("Red")]))
        player_table_rows = [html.Tr([html.Td(row["Player"]), html.Td(row["Goals"]), html.Td(row["Yellow Cards"]), html.Td(row["Red Cards"])]) for i, row in stats_df.iterrows()]
        player_table = html.Table([player_table_header, html.Tbody(player_table_rows)], className="table table-sm table-striped mt-3")
        
        team_player_summary = html.Div([
            html.H5([html.Img(src=get_flag_url(selected_team), style={"height": "24px", "marginRight": "8px", "verticalAlign": "middle"}), f"{selected_team}'s Journey in {selected_year}"], style={"color": "#1a5276"}),
            html.H6("Match Results", style={"marginTop": "15px"}), match_journey_table,
            html.H6("Player Statistics", style={"marginTop": "20px"}), player_table,
        ])

        all_time_matches = matches_df[
            (matches_df['Home Team Name'] == selected_team) | 
            (matches_df['Away Team Name'] == selected_team)
        ]

        # 2. Get the opponent from each of those matches.
        home_opponents = all_time_matches[all_time_matches['Home Team Name'] == selected_team]['Away Team Name']
        away_opponents = all_time_matches[all_time_matches['Away Team Name'] == selected_team]['Home Team Name']

        # 3. Combine them, find the unique values, and sort them.
        historical_opponents = sorted(pd.concat([home_opponents, away_opponents]).unique())
        
        # 4. Create the dropdown options from this filtered list.
        opponent_options = [{'label': team, 'value': team} for team in historical_opponents]

        # MODIFIED: When a team is selected, show the H2H panel
        card_style = {"border": "1px solid #d5dbdb", "padding": "20px", "borderRadius": "8px", "backgroundColor": "#ffffff", "boxShadow": "0 4px 8px rgba(0,0,0,0.05)", "marginBottom": "20px"}
        return team_player_summary, opponent_options, None, False, {'display': 'block', **card_style}

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
            return html.P("No all-time World Cup matches found between these two teams.")

        # --- 1. Calculate All Metrics ---
        team1_wins = ((h2h_matches['Home Team Name'] == team1) & (h2h_matches['Home Team Goals'] > h2h_matches['Away Team Goals'])).sum() + \
                     ((h2h_matches['Away Team Name'] == team1) & (h2h_matches['Away Team Goals'] > h2h_matches['Home Team Goals'])).sum()
        draws = (h2h_matches['Home Team Goals'] == h2h_matches['Away Team Goals']).sum()
        opponent_wins = len(h2h_matches) - team1_wins - draws
        
        team1_goals = h2h_matches.loc[h2h_matches['Home Team Name'] == team1, 'Home Team Goals'].sum() + h2h_matches.loc[h2h_matches['Away Team Name'] == team1, 'Away Team Goals'].sum()
        opponent_goals = h2h_matches.loc[h2h_matches['Home Team Name'] == opponent, 'Home Team Goals'].sum() + h2h_matches.loc[h2h_matches['Away Team Name'] == opponent, 'Away Team Goals'].sum()

        summary_text = f"Matches Played: {len(h2h_matches)}"
        
        # --- 2. Create the Mirrored Bar Chart Figure ---
        fig = go.Figure()

        # Add the POSITIVE trace for Wins/Draws
        fig.add_trace(go.Bar(
            x=[team1, 'Draw', opponent],
            y=[team1_wins, draws, opponent_wins],
            name='Wins / Draws',
            marker_color='#1f77b4',
            hovertemplate='%{x}: %{y} <extra></extra>'
        ))

        # Add the NEGATIVE trace for Goals Scored
        fig.add_trace(go.Bar(
            x=[team1, 'Draw', opponent],
            y=[-team1_goals, 0, -opponent_goals],  # Use negative values; 0 for Draw
            name='Goals Scored',
            marker_color='#ff7f0e',
            # Use customdata to show positive numbers on hover
            customdata=[team1_goals, 0, opponent_goals],
            hovertemplate='%{x}: %{customdata} Goals <extra></extra>'
        ))
        
        # --- 3. Format the Layout and Y-Axis ---
        
        # Find the max absolute value to make the y-axis symmetrical
        max_y_val = max(team1_wins, draws, opponent_wins, team1_goals, opponent_goals)
        tick_step = max(1, round(max_y_val / 4)) # Aim for ~4 ticks in each direction
        max_y_rounded = (int(max_y_val / tick_step) + 1) * tick_step if max_y_val > 0 else 5

        fig.update_layout(
            title='All-Time Head-to-Head Comparison',
            barmode='relative', # Essential for mirrored charts
            margin=dict(l=20, r=20, t=40, b=20),
            height=400,
            yaxis=dict(
                # Create custom tick labels to show positive numbers in the negative direction
                tickvals=[val for val in range(-max_y_rounded, max_y_rounded + 1, tick_step)],
                ticktext=[str(abs(val)) for val in range(-max_y_rounded, max_y_rounded + 1, tick_step)],
                title_text='Goals Scored <---- | ----> Wins / Draws',
                title_font=dict(size=12),
            ),
            xaxis=dict(
                # Ensure all categories are shown
                categoryorder='array',
                categoryarray=[team1, 'Draw', opponent]
            ),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )

        # --- 4. Return the new layout ---
        return html.Div([
            html.H5(f"All-Time Record: {team1} vs. {opponent}", style={"fontWeight":"bold"}),
            html.P(summary_text),
            dcc.Graph(figure=fig, style={'flex': 1})
        ])
    
    
    @app.callback(
        Output("team-selector-dropdown", "value", allow_duplicate=True),
        Input("world-map-choropleth", "clickData"),
        State("team-selector-dropdown", "options"),
        prevent_initial_call=True
    )
    def sync_dropdown_from_map_click(map_click, dropdown_options):
        """
        When a user clicks a country on the map, this callback updates the
        team selector dropdown's value, which in turn triggers the team details update.
        """
        if map_click is None:
            return no_update

        # Extract the clicked country name from the map's hover text
        clicked_country = map_click['points'][0]['hovertext']

        # Get a list of valid, selectable teams for the current tournament
        # from the dropdown's options.
        valid_teams = [option['value'] for option in dropdown_options]

        # Only update the dropdown if the clicked country is a valid participant
        # in the selected tournament. This prevents errors.
        if clicked_country in valid_teams:
            return clicked_country
        else:
            # If a non-participating country is clicked, do nothing.
            return no_update
