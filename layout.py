from dash import html, dcc
import pandas as pd

# ---------------------------------------------------------------------
# Common Plotly/Dash config used for all graphs so modebar is consistent
# ---------------------------------------------------------------------
COMMON_PLOTLY_CONFIG = {
    # show the modebar
    "displayModeBar": True,
    # remove the Plotly logo from the modebar
    "displaylogo": False,
    # exact buttons & order (single group array ensures the exact order)
    # Order: Pan, Zoom in, Zoom out, Zoom (box zoom / select), Download (toImage)
    "modeBarButtons": [
        ["pan2d", "zoomIn2d", "zoomOut2d", "zoom2d", "resetScale2d", "toImage"]
    ],
    # responsive layout behavior
    "responsive": True
}


def get_layout(world_cup_overview_df: pd.DataFrame):    
    years = world_cup_overview_df["Year"].dropna().astype(int).sort_values(ascending=False).unique()
    year_options = [{"label": str(year), "value": year} for year in years]

    # Styles
    container_style = {"maxWidth": "1200px", "margin": "20px auto", "padding": "10px"}
    card_style = {"border": "1px solid #e6e6e6", "padding": "18px", "borderRadius": "8px",
                  "backgroundColor": "#ffffff", "boxShadow": "0 2px 6px rgba(0,0,0,0.03)", "marginBottom": "18px"}
    header_style = {"textAlign": "center", "color": "#005a30", "fontWeight": "bold", "marginBottom": "6px"}
    subtitle_style = {"textAlign": "center", "color": "#333", "marginTop": "0px", "marginBottom": "16px"}

    # Bigger/bold sizes for plot titles (these are headings above the graph components)
    plot_title_style = {"fontSize": "20px", "fontWeight": "700", "marginTop": "0", "marginBottom": "6px", "color": "#222"}
    small_label = {"fontSize": "13px", "color": "#444", "marginBottom": "6px"}

    # Layout
    return html.Div([
        html.Div([
            html.H1("FIFA World Cup Data Analysis", style=header_style),
            html.P("Interactive dashboard to explore World Cup placements, matches and player-level events.", style=subtitle_style),

            # Top row: placements + controls
            html.Div([
                html.Div([
                    html.H3("Top-4 Placements by Country", style=plot_title_style),
                    html.P("Sorted by total top-4 finishes. Click on a country to inspect details.", style={"color":"#555", "marginBottom":"12px"}),
                    dcc.Graph(id="world-cup-placements-graph", config=COMMON_PLOTLY_CONFIG, style={"height": "520px"})
                ], style={**card_style, "flex":"1 1 65%"}),

                html.Div([
                    html.H4("Filter", style={"fontSize":"18px", "fontWeight":"700"}),
                    html.Div([html.Div("Select Year", style=small_label),
                              dcc.Dropdown(id="matches-year-selector", options=year_options,
                                           value=years[0] if len(years) > 0 else None, clearable=False,
                                           style={"width":"100%"})], style={"marginBottom":"12px"}),

                    # html.Div([html.Div("Year Range", style=small_label),
                    #           dcc.RangeSlider(id="year-range-slider",
                    #                           min=int(years.min()) if len(years) else 1930,
                    #                           max=int(years.max()) if len(years) else 2022,
                    #                           value=[int(years.min()), int(years.max())] if len(years) else [1930,2022],
                    #                           marks={int(year):str(int(year)) for i, year in enumerate(years) if i % max(1,len(years)//8)==0},
                    #                           tooltip={"placement":"bottom"})], style={"marginBottom":"18px"}),

                    # html.Div([html.Div("Stage Filter (optional)", style=small_label),
                    #           dcc.Checklist(id="stage-checklist", options=[], value=[], labelStyle={"display":"block"})], style={"marginBottom":"18px"}),
                ], style={**card_style, "flex":"1 1 32%"})
            ], style={"display":"flex", "gap":"16px", "flexWrap":"wrap"}),

            # Lower: goals + table
            html.Div([
                html.Div([
                    html.H3("Match Goals Overview", style=plot_title_style),
                    dcc.Graph(id="match-goals-graph", config=COMMON_PLOTLY_CONFIG, style={"height":"380px"})
                ], style={**card_style, "width":"100%"}),
                
                html.Div([
                    html.H3("Match Results Table", style=plot_title_style),
                    html.Div(id="match-details-table-container", style={"maxHeight":"420px", "overflowY":"auto"})
                ], style={**card_style, "width":"100%"})
            ], style={"marginTop":"8px", "display":"grid", "gridTemplateColumns":"1fr", "gap":"12px"}),

            html.Div("Data source: local CSV files (WorldCups.csv, WorldCupMatches.csv, WorldCupPlayers.csv).",
                     style={"textAlign":"center","color":"#666","fontSize":"13px","marginTop":"10px"})
        ], style=container_style)
    ])
