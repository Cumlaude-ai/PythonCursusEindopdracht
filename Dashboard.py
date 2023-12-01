import pathlib
import re
import json
from datetime import datetime
import flask
import dash
import matplotlib.colors as mcolors
import dash_bootstrap_components as dbc
from dash import dash_table
from dash import dcc
from dash import html
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input, State
import random
#from google.colab import output
from dateutil import relativedelta
import uuid
import sys

def make_marks_time_slider(mini, maxi):
    step = relativedelta.relativedelta(months=+1)
    start = datetime(year=mini.year, month=1, day=1)
    end = datetime(year=maxi.year, month=maxi.month, day=30)
    ret = {}

    current = start
    while current <= end:
        current_str = int(current.timestamp())
        if current.month == 1 and (current.year % 5 == 0 or current.year == datetime.now().year):
            ret[current_str] = {
                "label": str(current.year),
                "style": {"font-weight": "bold"},
            }

        else:
            pass
        current += step
    return ret
def dataFrameSize(dataframe, float_percent, visualColumn):
    #dataframe= pd.concat([pd.Series(xy[0]).reset_index(drop=True), pd.Series(xy[1]).reset_index(drop=True)], axis=1)
    dataframe = dataframe.sample(frac=float_percent, random_state=1,replace=True)
    grouped_monthYear_KNMI_df = dataframe.groupby(dataframe.index.year).mean()
    return grouped_monthYear_KNMI_df.index, grouped_monthYear_KNMI_df[visualColumn]
    
def time_slider_to_date(time_values):
    min_date = datetime.fromtimestamp(time_values[0]).strftime("%c")
    max_date = datetime.fromtimestamp(time_values[1]).strftime("%c")
    return [min_date, max_date]

def calculate_datespan(xy, time_values):
    dataframe= pd.concat([pd.Series(xy[0]).reset_index(drop=True), pd.Series(xy[1]).reset_index(drop=True)], axis=1)
    dataframe.iloc[:, 0]  = pd.to_datetime(dataframe.iloc[:, 0], format='%Y')
    if time_values is not None:
        min_date = time_values[0]
        max_date = time_values[1]
        dataframe = dataframe[
            (dataframe.iloc[:, 0]  >= pd.to_datetime(min_date))
            & (dataframe.iloc[:, 0] <= pd.to_datetime(max_date))
        ]
    return dataframe.iloc[:, 0], dataframe.iloc[:, 1]
    
def calculate_filter(dataframe, filter,visualColumn):
    dataframe = dataframe[dataframe["Datum"].dt.month == filter]
    grouped_monthYear_KNMI_df = dataframe.groupby(dataframe.index.year).mean()
        
    return grouped_monthYear_KNMI_df.index, grouped_monthYear_KNMI_df[visualColumn]
    
class interactiveGraph:
    def __init__(self,title,chartType,x,y,labels):
        self.title = title
        self.chartType = chartType
        self.x = x
        self.y = y
        self.labels = labels
        self.idlist = []
        self.configuration = []
    def addTimeframeSlider(self,title, subtitle,date_values):
        marks = make_marks_time_slider(date_values.min(), date_values.max())
        min_epoch = list(marks.keys())[0]
        max_epoch = list(marks.keys())[-1]
        sliderID = str(uuid.uuid1())
        slider = [
            html.Label(title, className="lead"),
            html.Div(dcc.RangeSlider(id=sliderID,marks=marks,min=min_epoch,max=max_epoch,step=(max_epoch - min_epoch) / (len(list(marks.keys())) * 3),value=[min_epoch, max_epoch])),
            html.P(
                subtitle,
                style={"fontSize": 10, "font-weight": "lighter","marginBottom": 40},
            ),
        ]
        self.configuration += slider
        self.idlist.append({"id":sliderID,"type":"timeslider", "data":date_values})
    def addPercentageSlider(self,title,subtitle, dataframe,visualColumn):
        sliderID = str(uuid.uuid1())
        slider =  [
            html.Label(title, className="lead"),
            html.P(
                subtitle,
                style={"fontSize": 10, "font-weight": "lighter"},
            ),
            dcc.Slider(
                id=sliderID,
                min=1,
                max=100,
                step=1,
                marks={
                    0: "0%",
                    10: "",
                    20: "20%",
                    30: "",
                    40: "40%",
                    50: "",
                    60: "60%",
                    70: "",
                    80: "80%",
                    90: "",
                    100: "100%",
                },
                value=100,
            )
        ]
        self.configuration += slider
        self.idlist.append({"id":sliderID,"type":"percentageslider","data":dataframe,"visualColumn":visualColumn})
    def addDropdown(self,title,subtitle,dataframe,visualColumn):
        dropdownID = str(uuid.uuid1())
        ret=[]
        counter =0
        for month in ["Januari", "Februari", "Maart", "April", "Mei", "Juni", "Juli", "Augustus", "September", "Oktober", "November", "December"]:
            counter += 1
            ret.append({"label": month, "value": counter})
        dropdown = [
            html.Label(title, style={"marginTop": 50}, className="lead"),
            html.P(
                subtitle,
                style={"fontSize": 10, "font-weight": "lighter"},
            ),
            dcc.Dropdown(
                id="MonthDropdown", clearable=False, style={"marginBottom": 50, "font-size": 12}, options=ret
            ),
        ]
        self.configuration += dropdown
        self.idlist.append({"id":"MonthDropdown","type":"dropdown","data":dataframe,"visualColumn":visualColumn})
class graph:
    def __init__(self,title,graph):
        self.title = title
        self.graph = graph
        
def createDashboard(Title,SiteUrl,LogoUrl,BackgroundUrl,Graphs):
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    graphList = []
    customGraphList = []
    for graph in Graphs:
        if isinstance(graph,interactiveGraph):
            interactivegraphID = str(uuid.uuid1())
            LEFT_COLUMN = html.Div(
                dbc.Container(
                    [
                        html.H4(children="Configuratie", className="display-5"),
                        html.Hr(className="my-2"),
                    ] + graph.configuration,
                    fluid=True,
                    className="py-3",
                ),
                className="p-2 mb-2 bg-light rounded-3",
            )

            CORROSPONDING_GRAPH = [
                dbc.CardHeader(html.H5(graph.title)),
                dbc.CardBody(
                    [
                        dcc.Loading(
                            children=[
                                dbc.Alert(
                                    "Not enough data to render this plot, please adjust the filters",
                                    color="warning",
                                    style={"display": "none"},
                                ),
                                dcc.Graph(id="InteractiveGraph",figure=graph.chartType(x=graph.x,y=graph.y,title=graph.title,labels=graph.labels)),
                            ],
                            type="default",
                        )
                    ],
                    style={"marginTop": 0, "marginBottom": 0},
                ),
            ]
            
            customGraphObject = dbc.Row(
                [
                    dbc.Col(LEFT_COLUMN, md=4, align="center"),
                    dbc.Col(dbc.Card(CORROSPONDING_GRAPH), md=8),
                ],
                style={"marginTop": 30},
            )
            customGraphList += [customGraphObject]
            for configobject in graph.idlist:
                if configobject["type"] == "dropdown":
                    @app.callback(
                        [Output("InteractiveGraph","figure",allow_duplicate=True)],
                        [Input(configobject["id"], "value")],
                        prevent_initial_call=True
                    )
                    def update_filter(dropdownValue):
                        x, y = calculate_filter(configobject["data"], dropdownValue,configobject["visualColumn"])
                        return [graph.chartType(x=x,y=y,title=graph.title,labels=graph.labels)]     
                        
                elif configobject["type"] == "percentageslider":
                    @app.callback(
                        [Output("InteractiveGraph","figure",allow_duplicate=True)],
                        [Input(configobject["id"], "value")],
                        prevent_initial_call=True
                        
                    )
                    def update_datasize(percentagesize):
                        dataFrameSizePercentage = float(percentagesize / 100)
                        x, y = dataFrameSize(configobject["data"], dataFrameSizePercentage,configobject["visualColumn"])
                        return [graph.chartType(x=x,y=y,title=graph.title,labels=graph.labels)]   
                        
                elif configobject["type"] == "timeslider":
                    @app.callback(
                        [Output("InteractiveGraph","figure",allow_duplicate=True)],
                        [Input(configobject["id"], "value")],
                        prevent_initial_call=True
                    )
                    def update_timeslider(time_values):
                        min_date, max_date = time_slider_to_date(time_values)
                        x, y = calculate_datespan([graph.x,graph.y], [min_date, max_date])
                        
                        return [graph.chartType(x=x,y=y,title=graph.title,labels=graph.labels)]    
        else:
            GRAPH_PLOT = [
                dbc.Card([
                    dbc.CardHeader(html.H5(graph.title)),
                    dbc.Alert(
                        "Niet genoeg data om plot te renderen",
                        color="warning",
                        style={"display": "none"},
                    ),
                    dbc.CardBody(
                        [
                            dbc.Row(
                                [
                                    dcc.Loading(
                                      children=[
                                          dcc.Graph(figure=graph.graph)
                                          ],
                                      type="default",
                                    ),
                                ]
                            )
                        ]
                    ),
                ],style={"marginTop": 30},),
            ]
            graphList += GRAPH_PLOT
            
    NAVBAR = dbc.Navbar(
        children=[
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=LogoUrl, height="50px")),
                        dbc.Col(
                            dbc.NavbarBrand(Title, className="ml-2")
                        ),
                    ],
                    align="center",
                ),
                href=SiteUrl,
                style={"text-decoration": "none"},
            )
        ],
        color="dark",
        dark=True,
        sticky="top",
        style={"background-size":"cover","color":"white","background-image":"url('"+BackgroundUrl+"')"},
    )
    
    BODY = dbc.Container(
        graphList + customGraphList,
        className="mt-12",
    )

    WATERMARK = dbc.Container(
        children=[
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src="https://github.com/Cumlaude-ai/Python_Cursus/blob/main/data/CumlaudeAI.png?raw=true", height="50px")),
                    ],
                    align="center",
                ),
                href="https://cumalaude.ai",
                style={"text-decoration": "none"},
            )
        ],
        style={"bottom":"0px","right":"50px","display": "flex","justify-content": "flex-end","background-color": "#ebebeb","width": "min-content","margin-left": "auto","margin-right": "50px","border-radius": "10px 10px 0px 0px","padding-top": "10px","opacity": "0.3","position":"fixed"},
        className="watermark",
    )
    
    app.layout = html.Div(children=[NAVBAR, BODY,WATERMARK])

    
        
    return app.run(jupyter_mode="external",debug=False)#, output.serve_kernel_port_as_iframe(8050)
