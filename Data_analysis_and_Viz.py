# Required Python Modules
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from dash import dash_table
import statsmodels.api as sm


# Load the dataset
df = pd.read_csv("countries_gdp.csv")

# Data Cleaning
df = df.dropna()  # Drop rows with missing values

# Data Analysis
# Descriptive Statistics
df_stats = df.describe()

# Bivariate Analysis
correlation = df['GDP ($ per capita)'].corr(df['Literacy (%)'])
regression = sm.OLS(df['GDP ($ per capita)'], sm.add_constant(df['Literacy (%)'])).fit()

# Cluster Analysis
cluster_df = df[['Climate', 'Pop. Density (per sq. mi.)', 'Coastline (coast/area ratio)']]

# Factor Analysis
factor_analysis_df = df[['GDP ($ per capita)', 'Literacy (%)', 'Phones (per 1000)', 'Arable (%)', 'Service']]

# Visualization using Dash Plotly
app = dash.Dash(__name__)

# Define available descriptive statistics options
descriptive_stats_options = [
    {'label': 'Mean', 'value': 'mean'},
    {'label': 'Median', 'value': 'median'},
    {'label': 'Standard Deviation', 'value': 'std'},
    # Add more options as needed
]

# App Layout
app.layout = html.Div([
    html.H1("Data Analysis and Visualization"),
    
    # Descriptive Statistics
    html.H2("Descriptive Statistics"),
    
    dcc.Dropdown(
        id='stats-dropdown',
        options=descriptive_stats_options,
        value='mean',  # Default selected option
        style={'width': '200px'}
    ),
    
    dash_table.DataTable(
        id='descriptive-stats-table',
        columns=[{'name': col, 'id': col} for col in df_stats.columns],
        data=df_stats.to_dict('records'),
        style_table={'overflowX': 'auto'},
    ),

    # Bivariate Analysis
    html.H2("Bivariate Analysis"),
    dcc.Graph(
        id='bivariate-graph',
        figure={
            'data': [
                go.Scatter(
                    x=df['Literacy (%)'],
                    y=df['GDP ($ per capita)'],
                    mode='markers',
                    name='Data Points'
                ),
                go.Scatter(
                    x=df['Literacy (%)'],
                    y=regression.predict(sm.add_constant(df['Literacy (%)'])),
                    mode='lines',
                    name='Regression Line'
                )
            ],
            'layout': {'title': 'GDP per Capita vs Literacy Rate'}
        }
    ),
    html.P(f"Correlation: {correlation}"),

    # Cluster Analysis
    html.H2("Cluster Analysis"),
    html.P("Select variables for cluster analysis:"),
    dcc.Dropdown(
        id='cluster-variable-dropdown',
        options=[
            {'label': 'Climate', 'value': 'Climate'},
            {'label': 'Population Density', 'value': 'Pop. Density (per sq. mi.)'},
            {'label': 'Coastline Ratio', 'value': 'Coastline (coast/area ratio)'}
        ],
        value='Climate'
    ),
    dcc.Graph(id='cluster-graph'),

    # Factor Analysis
    html.H2("Factor Analysis"),
    html.P("Select variables for factor analysis:"),
    dcc.Dropdown(
        id='factor-variable-dropdown',
        options=[
            {'label': 'GDP per Capita', 'value': 'GDP ($ per capita)'},
            {'label': 'Literacy Rate', 'value': 'Literacy (%)'},
            {'label': 'Phones per 1000', 'value': 'Phones (per 1000)'},
            {'label': 'Arable Land', 'value': 'Arable (%)'},
            {'label': 'Service Sector', 'value': 'Service'}
        ],
        value='GDP ($ per capita)'
    ),
    dcc.Graph(id='factor-graph'),

    # World Map
    html.H2("World Map"),
    dcc.Graph(id='world-map')
])


# Callback for Cluster Analysis Graph
@app.callback(
    Output('cluster-graph', 'figure'),
    [Input('cluster-variable-dropdown', 'value')]
)
def update_cluster_graph(selected_variable):
    # Generate the cluster analysis graph based on the selected variable
    cluster_graph = px.scatter(cluster_df, x='Climate', y=selected_variable, color='Climate')
    return cluster_graph


# Callback for Factor Analysis Graph
@app.callback(
    Output('factor-graph', 'figure'),
    [Input('factor-variable-dropdown', 'value')]
)
def update_factor_graph(selected_variable):
    # Generate the factor analysis graph based on the selected variable
    factor_graph = px.scatter(factor_analysis_df, x=selected_variable, y='GDP ($ per capita)', trendline="ols")
    return factor_graph


# Callback for World Map
@app.callback(
    Output('world-map', 'figure'),
    [Input('factor-variable-dropdown', 'value')]
)
def update_world_map(selected_variable):
    # Generate the world map with GDP per capita
    gdp_map = px.choropleth(df, locations='Country', locationmode='country names',
                            color=selected_variable,
                            color_continuous_scale='viridis',
                            labels={selected_variable: 'GDP per capita'},
                            title='GDP per capita by Country')
    return gdp_map

# Callback for updating descriptive statistics table based on the selected option
@app.callback(
    Output('descriptive-stats-table', 'data'),
    [Input('stats-dropdown', 'value')]
)
def update_descriptive_stats_table(selected_stat):
    if selected_stat == 'mean':
        table_data = df_stats.loc['mean'].to_dict()
    elif selected_stat == 'median':
        table_data = df_stats.loc['50%'].to_dict()
    elif selected_stat == 'std':
        table_data = df_stats.loc['std'].to_dict()
    else:
        table_data = df_stats.loc['mean'].to_dict()

    return [table_data]

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
