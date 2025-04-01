import numpy as np
import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Step 1: Create the dataset
def create_worldcup_dataset():
    # Data from Wikipedia as of knowledge cutoff
    data = {
        'Year': [1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966, 1970, 1974, 
                 1978, 1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022],
        'Winner': ['Uruguay', 'Italy', 'Italy', 'Uruguay', 'West Germany', 'Brazil', 
                   'Brazil', 'England', 'Brazil', 'West Germany', 'Argentina', 
                   'Italy', 'Argentina', 'West Germany', 'Brazil', 'France', 
                   'Brazil', 'Italy', 'Spain', 'Germany', 'France', 'Argentina'],
        'Runner-up': ['Argentina', 'Czechoslovakia', 'Hungary', 'Brazil', 'Hungary', 
                      'Sweden', 'Czechoslovakia', 'West Germany', 'Italy', 
                      'Netherlands', 'Netherlands', 'West Germany', 'West Germany', 
                      'Argentina', 'Italy', 'Brazil', 'Germany', 'France', 
                      'Netherlands', 'Argentina', 'Croatia', 'France'],
        'Score': ['4-2', '2-1 (a.e.t.)', '4-2', '2-1', '3-2', '5-2', '3-1', '4-2 (a.e.t.)',
                  '4-1', '2-1', '3-1 (a.e.t.)', '3-1', '3-2', '1-0', '0-0 (a.e.t.) (3-2 p.)',
                  '3-0', '2-0', '1-1 (a.e.t.) (5-3 p.)', '1-0 (a.e.t.)', '1-0 (a.e.t.)',
                  '4-2', '3-3 (a.e.t.) (4-2 p.)']
    }
    
    df = pd.DataFrame(data)
    
    # Combine West Germany and Germany
    df.replace({'West Germany': 'Germany'}, inplace=True)
    
    return df

# Create the dataset
worldcup_df = create_worldcup_dataset()

# Create a country-code mapping (ISO Alpha-3 codes)
country_codes = {
    'Argentina': 'ARG',
    'Brazil': 'BRA',
    'England': 'GBR',
    'France': 'FRA',
    'Germany': 'DEU',
    'Italy': 'ITA',
    'Spain': 'ESP',
    'Uruguay': 'URY',
    'Czechoslovakia': 'CZE',  # Using Czech Republic code for historical Czechoslovakia
    'Hungary': 'HUN',
    'Sweden': 'SWE',
    'Netherlands': 'NLD',
    'Croatia': 'HRV'
}

# Add country codes to the dataframe
worldcup_df['Winner_Code'] = worldcup_df['Winner'].map(country_codes)
worldcup_df['Runner-up_Code'] = worldcup_df['Runner-up'].map(country_codes)

# Calculate win counts
win_counts = worldcup_df['Winner'].value_counts().reset_index()
win_counts.columns = ['Country', 'Wins']
win_counts['Code'] = win_counts['Country'].map(country_codes)

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Define the layout
app.layout = html.Div([
    html.H1("FIFA World Cup Winners Dashboard", style={'textAlign': 'center'}),
    
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': country, 'value': country} 
                         for country in sorted(worldcup_df['Winner'].unique())],
                placeholder="Select a country to view its wins",
                clearable=True
            )
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': year, 'value': year} 
                         for year in sorted(worldcup_df['Year'], reverse=True)],
                placeholder="Select a year to view the finalists",
                clearable=True
            )
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),
    
    html.Div([
        dcc.Graph(id='choropleth-map', style={'height': '500px'})
    ]),
    
    html.Div(id='country-info', style={'marginTop': '20px'}),
    html.Div(id='year-info', style={'marginTop': '20px'})
])

# Callbacks for interactivity
@app.callback(
    [Output('choropleth-map', 'figure'),
     Output('country-info', 'children'),
     Output('year-info', 'children')],
    [Input('country-dropdown', 'value'),
     Input('year-dropdown', 'value')]
)
def update_dashboard(selected_country, selected_year):
    # Default map shows all winners
    fig = px.choropleth(
        win_counts,
        locations="Code",
        color="Wins",
        hover_name="Country",
        hover_data={"Code": False, "Wins": True},
        color_continuous_scale=px.colors.sequential.Plasma,
        title="FIFA World Cup Wins by Country"
    )
    
    fig.update_geos(showcoastlines=True, coastlinecolor="Black")
    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
    
    # Highlight selected country if one is chosen
    if selected_country:
        country_data = win_counts[win_counts['Country'] == selected_country]
        if not country_data.empty:
            fig.add_trace(
                go.Choropleth(
                    locations=country_data['Code'],
                    z=country_data['Wins'],
                    colorscale=[[0, 'red'], [1, 'red']],
                    showscale=False,
                    hoverinfo='none'
                )
            )
    
    # Country info output
    country_output = ""
    if selected_country:
        wins = worldcup_df[worldcup_df['Winner'] == selected_country]
        if not wins.empty:
            win_years = ", ".join(map(str, sorted(wins['Year'])))
            country_output = html.Div([
                html.H3(f"{selected_country} World Cup Wins"),
                html.P(f"Total Wins: {len(wins)}"),
                html.P(f"Years Won: {win_years}")
            ])
    
    # Year info output
    year_output = ""
    if selected_year:
        final = worldcup_df[worldcup_df['Year'] == selected_year]
        if not final.empty:
            year_output = html.Div([
                html.H3(f"{selected_year} World Cup Final"),
                html.P(f"Winner: {final['Winner'].values[0]}"),
                html.P(f"Runner-up: {final['Runner-up'].values[0]}"),
                html.P(f"Score: {final['Score'].values[0]}")
            ])
    
    return fig, country_output, year_output

if __name__ == '__main__':
    app.run(debug=True, port=8051)  