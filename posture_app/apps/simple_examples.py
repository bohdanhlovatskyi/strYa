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

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets").resolve()

modes_list = ["Steady", "Forward rotation", "Forward tilt", "Forward tilt and rotation", "Side tilt"]

modes_dict = {"Steady": "angles_steady.csv", "Forward rotation": "angles_forward_rotation.csv",
"Forward tilt": "angles_forward_tilt.csv", "Forward tilt and rotation": "angles_forward_tilt_and_rotation.csv",
"Side tilt": "angles_side_tilt.csv"}

videos_dict = {"Steady": "https://youtu.be/dsJy6R1AejI", "Forward rotation": "https://youtu.be/VjDsmIdoKyk",
"Forward tilt": "https://youtu.be/YzQ5LT6rhYw", "Forward tilt and rotation": "https://youtu.be/UZj-L4j23qw",
"Side tilt": "https://youtu.be/9oCsNgZ29jU"}

layout = html.Div([
    html.H1('strYa', style={"textAlign": "center", "color": "#8A2BE2"}),

    html.Div([
        html.Div(dcc.Dropdown(
            id='posture_mode', value='Steady', clearable=False,
            options=[{'label': x, 'value': x} for x in modes_list]
        ), className='six columns')
    ], className='row'),

    html.Div([
        html.Div(dcc.Graph(
            id='six_graphs', 
            figure={}
        ), style={'display': 'inline-block', 'width': '49%'}),
        html.Div(id='video_field',
            children={}, 
            style={'display': 'inline-block', 'width': '49%'})
    ])
    
])


@app.callback(
    [Output(component_id='six_graphs', component_property='figure'),
    Output(component_id='video_field', component_property='children')],
    Input(component_id='posture_mode', component_property='value')
)
def display_value(mode_chosen):
    df = pd.read_csv(DATA_PATH.joinpath(modes_dict[mode_chosen]))
    rounded = np.round(df)


    fig = make_subplots(
    rows=2, cols=2, subplot_titles=("x1 graph", "x2 graph", "y1 graph", "y2 graph")
)
    #find optimal and delete it from data frame
    optimal = df.tail(1)
    x1_optimal = optimal['x1'].tolist()[0]
    y1_optimal = optimal['y1'].tolist()[0]
    x2_optimal = optimal['x2'].tolist()[0]
    y2_optimal = optimal['y2'].tolist()[0]
    df = df.head(-1)

    #find all par for graphs
    time = df['computer_time'].tolist()
    start_time = time[0]
    time = [i-start_time for i in time]
    x1 = df['x1'].tolist()
    x1 = [i+x1_optimal for i in x1]
    y1 = df['y1'].tolist()
    y1 = [i-y1_optimal for i in y1]

    x2 = df['x2'].tolist()
    x2 = [i+x2_optimal for i in x2]
    y2 = df['y2'].tolist()
    y2 = [i-y2_optimal for i in y2]

    # Add traces
    fig.add_trace(go.Scatter(x=time, y=x1), row=1, col=1)
    fig.add_trace(go.Scatter(x=time, y=y1), row=2, col=1)

    fig.add_trace(go.Scatter(x=time, y=x2), row=1, col=2)
    fig.add_trace(go.Scatter(x=time, y=y2), row=2, col=2)


    # Update xaxis properties
    fig.update_xaxes(title_text="time", row=1, col=1)
    fig.update_xaxes(title_text="time", row=2, col=1)

    fig.update_xaxes(title_text="time", row=1, col=2)
    fig.update_xaxes(title_text="time", row=2, col=2)

    # # Update yaxis properties
    fig.update_yaxes(title_text="x1", row=1, col=1, range=[-90, 90])
    fig.update_yaxes(title_text="y1", row=2, col=1, range=[-90, 90])

    fig.update_yaxes(title_text="x2", row=1, col=2, range=[-90, 90])
    fig.update_yaxes(title_text="y2", row=2, col=2, range=[-90, 90])


    # Update title and height
    fig.update_layout(title_text="Posture position", height=500, width=600)

    video = player.DashPlayer(
            id="video-display",
            url=videos_dict[mode_chosen],
            controls=True,
            playing=False,
            volume=1,
            width="600px",
            height="450px",)
    return fig, video
