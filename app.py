#### Exploring linear models for prediction
# -*- coding: utf-8 -*-

# Run this app with `python app3.py` and
# visit http://127.0.0.1:8050/ in your web browser.
# documentation at https://dash.plotly.com/ 

# based on ideas at "Dash App With Multiple Inputs" in https://dash.plotly.com/basic-callbacks
# plotly express line parameters via https://plotly.com/python-api-reference/generated/plotly.express.line.html#plotly.express.line

from flask import Flask
from os import environ

import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
# plotly express could be used for simple applications
# but this app needs to build plotly graph components separately 
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = Flask(__name__)
app = dash.Dash(
    server=server,
    url_base_pathname=environ.get('JUPYTERHUB_SERVICE_PREFIX', '/'),
    external_stylesheets=external_stylesheets
)

##################################
# Fetch and prep the data
# read in the data from the prepared CSV file. 
co2_data_source = "./data/monthly_in_situ_co2_mlo.csv"
co2_data_full = pd.read_csv(
    co2_data_source, skiprows=np.arange(0, 56), na_values="-99.99"
)

co2_data_full.columns = [
    "year", "month", "date_int", "date", "raw_co2", "seasonally_adjusted",
    "fit", "seasonally_adjusted_fit", "co2 filled", "seasonally_adjusted_filled" 
]

# for handling NaN's see https://pandas.pydata.org/pandas-docs/stable/user_guide/missing_data.html
co2_data = co2_data_full.dropna()

# A linear model with slope and intercept to predict CO2
def predict_co2(slope, intercept, initial_date, prediction_date):
    a = slope * (prediction_date-initial_date) + intercept
    
    return a

##################################
# Lay out the page 
app.layout = html.Div([
# Introduction
    dcc.Markdown('''
        ### Approximate linear models for CO2 at MonaLoa, Hawaii

        #### Instructions 

        Adjust straight line's slope and intercept to fit a "linear model" to the first 5 years of data, then again to most recent 5 years of data. 
        Do these two linear approximations to the process predict the same CO2 concentration
        for the year 2030? Predicted value in ppm is given in the plot title above the graph. 
        _(NOTE: interactive graph controls appear when mouse is over the graph.)_

        Smaller slope values "flatten" the line. Smaller line intercepts drop the line down. 
        If the orange line is not visible display all data, bring line to roughly the right place
        and then change to first or last 5 years of data to fine tune your linear fit. 
        
        '''),
    # controls for plot
    html.Div([
        dcc.Markdown(''' **_Slope:_** '''),
        dcc.Slider(
            id='line_slope', min=0, max=3, step=0.05, value=2,
            marks={0:'0', 0.5:'0.5', 1:'1', 1.5:'1.5', 2:'2', 2.5:'2.5', 3:'3'},
            tooltip={'always_visible':True, 'placement':'topLeft'}
        ),
    ], style={'width': '48%', 'display': 'inline-block'}),
    
    html.Div([
        dcc.Markdown(''' **_Intercept:_** '''),
        dcc.Slider(
            id='line_intcpt', min=250, max=320, step=0.25,value=312,
            marks={250:'250', 260:'260', 270:'270', 280:'280', 290:'290', 300:'300', 310:'310', 320:'320'},
            tooltip={'always_visible':True, 'placement':'topLeft'}
        ),
    ], style={'width': '48%', 'display': 'inline-block'}),
    
# start and end year of plot 
# NOT NEEDED IF USING 1ST AND LAST 5 YEAR RADIO BUTTONS.   
#    html.Div([
#        dcc.Markdown(''' _Start:_ '''),
#        dcc.Slider(
#            id='start', min=1958, max=2019, step=1, value=1958,
#            marks={1960:'1960', 1970:'1970', 1980:'1980', 1990:'1990', 2000:'2000', 2010:'2010',2020:'2020'},
#            tooltip={'always_visible':True, 'placement':'topLeft'}
#        ),
#    ], style={'width': '48%', 'display': 'inline-block'}),
#    
#    html.Div([
#        dcc.Markdown(''' _End (**> Start!**):_ '''),
#        dcc.Slider(
#            id='end', min=1960, max=2030, step=1, value=1963,
#            marks={1960:'1960', 1970:'1970', 1980:'1980', 1990:'1990', 2000:'2000', 2010:'2010',2020:'2020'},
#            tooltip={'always_visible':True, 'placement':'topLeft'}
#        ),
#    ], style={'width': '48%', 'display': 'inline-block'}),

    html.Div([
        dcc.Markdown(''' **_Signal type:_** '''),
         dcc.RadioItems(
            id='Data_type',
            options=[
            {'label': 'Seasonally adjusted data', 'value': 'adj'},
            {'label': 'Raw data', 'value': 'raw'}
            ],
            value='adj'
        ),
    ], style={'width': '48%', 'display': 'inline-block'}),

# Done this way to make easier to set appropriate y-axis limits
# Could use sliders commented out above if y-axis limits are set by calculating range for years-span
     html.Div([
       # dcc.Markdown(''' 
       # _Choose first or last 5 years of data_         
       # '''),
         dcc.RadioItems(
            id='zone',
            options=[
            {'label': '1st 5 years', 'value': '1st5yrs'},
            {'label': 'last 5 years', 'value': 'last5yrs'},
            {'label': 'All data', 'value': 'alldata'}
            ],
            value='1st5yrs'
        ),
    ], style={'width': '48%', 'display': 'inline-block'}),

# after controls, place plot
    dcc.Graph(id='graph'),

# closing text
    dcc.Markdown('''
    -------

    ### Discussion

    Within small enough regions, the data follow an approximately linear trend, 
    so a linear model has some predictive power. To consider these questions, 
    revisit the linear fit for "early" and "recent" 5 year periods.
    
    1. Out to which year would you trust the model built with the data from 1958 - 1963? 
    2. Where does it start to break down?
    3. How far out would you trust our predictions with data from 2015 - 2020? Would you trust our model to predict CO$_2$ in the year 2050? 
    4. How might you approach building a model to fit all of our data? 
    5. Given what the "raw data" look like, what do you think "seasonaly adjusted" means? 
    6. Use the graph's "Camera" icon to make a PNG file of your graph with all data and linear model fitting the first 5 years.
    7. Do the same for your graph with linear model fitting the last 5 years of data. Hand both in for assessment. 

    ### Attribution
    
    * Derived from [L. Heagy's presentation](https://ubc-dsci.github.io/jupyterdays/sessions/heagy/widgets-and-dashboards.html) at UBC's Jupyter Days 2020, which in turn is adapted from the [Intro-Jupyter tutorial from ICESat-2Hackweek](https://github.com/ICESAT-2HackWeek/intro-jupyter), which has contributions from: [Shane Grigsby (@espg)](https://github.com/espg), [Lindsey Heagy (@lheagy)](https://github.com/lheagy), 
    [Yara Mohajerani (@yaramohajerani)](https://github.com/yaramohajerani), 
    and [Fernando Pérez (@fperez)](https://github.com/fperez). 
    * This version, code by F. Jones.
    * Original data are at the [Scripps CO2 program](https://scrippsco2.ucsd.edu/data/atmospheric_co2/primary_mlo_co2_record.html). See the NOAA [Global Monitoring Laboratory](https://www.esrl.noaa.gov/gmd/ccgg/trends/) for additional details.
    
    '''),
], style={'width': '900px'}
)

# end of layout and definition of controls.
##################################
# The callback function with it's app.callback wrapper.
@app.callback(
    Output('graph', 'figure'),
    Input('line_slope', 'value'),
    Input('line_intcpt', 'value'),
    Input('Data_type', 'value'),
#    Input('start', 'value'),
#    Input('end', 'value'),
    Input('zone', 'value'),
    )
#def update_graph(line_slope, line_intcpt, Data_type, start, end, zone):
def update_graph(line_slope, line_intcpt, Data_type, zone):
# construct all the figure's components
    plot = go.Figure()

    l1 = line_slope * (co2_data.date - np.min(co2_data.date)) + line_intcpt

    if Data_type == 'raw':
        plot.add_trace(go.Scatter(x=co2_data.date, y=co2_data.raw_co2, mode='markers',
            line=dict(color='MediumTurquoise'), name="CO2"))
    if Data_type == 'adj':
        plot.add_trace(go.Scatter(x=co2_data.date, y=co2_data.seasonally_adjusted, mode='markers',
            line=dict(color='MediumTurquoise'), name="CO2"))
    
    plot.add_trace(go.Scatter(x=co2_data.date, y=l1, mode='lines',
        line=dict(color='SandyBrown'), name="linear fit"))
    
    plot.update_layout(xaxis_title='Year', yaxis_title='ppm')
#    plot.update_xaxes(range=[start, end])
    
    if zone == '1st5yrs':
        plot.update_xaxes(range=[1958, 1963])
        plot.update_yaxes(range=[312, 322])

    if zone == 'last5yrs':
        plot.update_xaxes(range=[2015, 2020])
        plot.update_yaxes(range=[395, 415])
    
    if zone == 'alldata':
        plot.update_xaxes(range=[1955, 2023])
        plot.update_yaxes(range=[310, 440])

    predicted_co2 = predict_co2(line_slope, line_intcpt, 1958, 2030)
    plot.layout.title = f"Predicted CO2 for {2030}: {predicted_co2:1.2f} ppm."

    return plot

if __name__ == '__main__':
    app.run_server(debug=True)
