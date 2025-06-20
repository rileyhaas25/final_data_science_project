# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
print(spacex_df.columns)
# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown', options=(
                                    [{'label': 'All Sites', 'value': 'ALL'}] +
                                    [{'label': s, 'value': s} for s in sorted(spacex_df['Launch Site'].unique())]
                                    ),
                                    value='ALL',
                                    placeholder="Select a Launch Site here",
                                    searchable=True
                                    ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000, 
                                                marks={i: str(i) for i in range(0, 10001, 2000)}, 
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # count successes per site
        fig = px.pie(
            spacex_df,
            names='Launch Site',
            values='class',
            title='Total Successful Launches by Site'
        )
    else:
        # filter to the chosen site
        df = spacex_df[spacex_df['Launch Site'] == selected_site]
        counts = df['class'].value_counts().reset_index()
        counts.columns = ['class', 'count']
        counts['outcome'] = counts['class'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(
            counts,
            names='outcome',
            values='count',
            title=f'Success vs. Failure for {selected_site}'
        )
    return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")]
)
def update_scatter_chart(selected_site, payload_range):
    # unpack payload slider
    low, high = payload_range

    # 1) filter by payload range
    mask = (
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    )
    filtered_df = spacex_df[mask]

    # 2) if a specific site is chosen, filter that too
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    # 3) build the scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=(
            "Correlation between Payload and Success "
            + (f"for {selected_site}" if selected_site!='ALL' else "for All Sites")
        ),
        labels={'class':'Launch Outcome'}
    )
    return fig
# Run the app
if __name__ == '__main__':
    app.run()
