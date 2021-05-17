import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import pathlib
from app import app

import plotly as py
from plotly.subplots import make_subplots
import plotly.graph_objects as go

import dash_player as player

import numpy as np
import time as t

labels = ['steady','forward_tilt','side_tilt','forward_rotation']
values = [390, 161, 97, 52]

# pull is given as a fraction of the pie radius
fig = go.Figure(data=[go.Pie(labels=labels, values=values, pull=[0.2, 0, 0, 0])])

video = player.DashPlayer(
    id="main_video.mp4",
    url='https://youtu.be/XFHD3lotkfY',
    controls=True,
    playing=False,
    volume=1,
    width="650px",
    height="500px",)


layout = html.Div([
    html.H1('strYa', style={"textAlign": "center", "color": "#8A2BE2"}),

    html.Div([
        html.Div(dcc.Graph(
            id='graphs_timeline', 
            figure=fig
        ), style={'display': 'inline-block', 'width': '49%'}),
        html.Div(id='video',
            children=video, 
            style={'display': 'inline-block', 'width': '49%'})
    ])
    
])
