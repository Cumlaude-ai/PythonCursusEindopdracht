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
from google.colab import output
from dateutil import relativedelta

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
        
class interactiveGraph:
    def __init__(self,title,graph):
        self.title = title
        self.graph = graph
        self.TimeframeSlider = []
    def addTimeframeSlider(min_date,max_date):
        marks = make_marks_time_slider(min_date, max_date)
        min_epoch = list(marks.keys())[0]
        max_epoch = list(marks.keys())[-1]
        self.TimeframeSlider.append(html.Div(dcc.RangeSlider(marks=marks,min=min_epoch,max=max_epoch,step=(max_epoch - min_epoch) / (len(list(marks.keys())) * 3),value=[min_epoch, max_epoch])))

class graph:
    def __init__(self,title,graph):
        self.title = title
        self.graph = graph
        
def createDashboard(Title,SiteUrl,LogoUrl,BackgroundUrl,Data,Graphs):
    graphList = []
    customGraphList = []
    return Graphs
    for graph in Graphs:
        print(graph)
        if isinstance(graph,interactiveGraph):
            LEFT_COLUMN = html.Div(
                dbc.Container(
                    [
                        html.H4(children="Configuratie", className="display-5"),
                        html.Hr(className="my-2"),
                        html.Label("Selecteer percentage van de dataset", className="lead"),
                        html.P(
                            "(Lager is sneller, hoger is preciezer)",
                            style={"fontSize": 10, "font-weight": "lighter"},
                        ),
                        dcc.Slider(
                            id="n-selection-slider",
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
                            value=20,
                        ),
                        html.Label("Selecteer een maand", style={"marginTop": 50}, className="lead"),
                        html.P(
                            "(Je kan de dropdown gebruiken of klikken op het staafdiagram hiernaast.)",
                            style={"fontSize": 10, "font-weight": "lighter"},
                        ),
                        dcc.Dropdown(
                            id="bank-drop", clearable=False, style={"marginBottom": 50, "font-size": 12}
                        ),
                        html.Label("Selecteer tijd frame", className="lead"),
                        html.Div(dcc.RangeSlider(id="time-window-slider")),
                        html.P(
                            "(Je kan het tijdframe per maand bepalen)",
                            style={"fontSize": 10, "font-weight": "lighter","marginBottom": 40},
                        ),
                    ],
                    fluid=True,
                    className="py-3",
                ),
                className="p-2 mb-2 bg-light rounded-3",
            )

            CORROSPONDING_GRAPH = [
                dbc.CardHeader(html.H5("Regenval per maand")),
                dbc.CardBody(
                    [
                        dcc.Loading(
                            id="loading-banks-hist",
                            children=[
                                dbc.Alert(
                                    "Not enough data to render this plot, please adjust the filters",
                                    id="no-data-alert-bank",
                                    color="warning",
                                    style={"display": "none"},
                                ),
                                dcc.Graph(id="bank-sample",figure=emptyGraph),
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
            customGraphList.append(customGraphObject)
        else:
            GRAPH_PLOT = [
                dbc.CardHeader(html.H5(graph.title)),
                dbc.Alert(
                    "Niet genoeg data om plot te renderen",
                    id="no-data-alert",
                    color="warning",
                    style={"display": "none"},
                ),
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dcc.Loading(
                                  id="loading-treemap",
                                  children=[
                                      dcc.Graph(figure=graph.graph)
                                      ],
                                  type="default",
                                ),
                            ]
                        )
                    ]
                ),
            ]
            graphList.append(GRAPH_PLOT)
            print(graphList)
            
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
    
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout = html.Div(children=[NAVBAR, BODY])
    
    def dataFrameSize(dataframe, float_percent):
        print("making a local_df data sample with float_percent: %s" % (float_percent))
        return dataframe.sample(frac=float_percent, random_state=1,replace=True)
    
    def time_slider_to_date(time_values):
        min_date = datetime.fromtimestamp(time_values[0]).strftime("%c")
        max_date = datetime.fromtimestamp(time_values[1]).strftime("%c")
        return [min_date, max_date]
    
    def calculate_bank_sample_data(dataframe, time_values):
        if time_values is not None:
            min_date = time_values[0]
            max_date = time_values[1]
            dataframe = dataframe[
                (dataframe["Datum"] >= min_date)
                & (dataframe["Datum"] <= max_date)
            ]
    
        yearData = dataframe.groupby(dataframe.index.year)
        years = yearData["Datum"].groups.keys()
        avgRain = yearData["Etmaalsom neerslag"].mean().round(0).astype(np.int64).tolist()
    
        return years, avgRain
    
    @app.callback(
        [
            Output("time-window-slider", "marks"),
            Output("time-window-slider", "min"),
            Output("time-window-slider", "max"),
            Output("time-window-slider", "step"),
            Output("time-window-slider", "value"),
        ],
        [Input("n-selection-slider", "value")],
    )
    def populate_time_slider(value):
        value += 0
        min_date = KNMI_2000_Regen_df["Datum"].min()
        max_date = KNMI_2000_Regen_df["Datum"].max()
    
        app.logger.info(min_date)
        app.logger.info(max_date)
        marks = make_marks_time_slider(min_date, max_date)
        app.logger.info(marks)
        min_epoch = list(marks.keys())[0]
        max_epoch = list(marks.keys())[-1]
    
        return (
            marks,
            min_epoch,
            max_epoch,
            (max_epoch - min_epoch) / (len(list(marks.keys())) * 3),
            [min_epoch, max_epoch],
        )
    
    @app.callback(
        Output("bank-drop", "options"),
        [Input("time-window-slider", "value"), Input("n-selection-slider", "value")],
    )
    def populate_bank_dropdown(time_values, n_value):
        """ TODO """
        print("bank-drop: TODO USE THE TIME VALUES AND N-SLIDER TO LIMIT THE DATASET")
        if time_values is not None:
            pass
        n_value += 1
        #months, rain = get_rain_by_month(Grouped_KNMI)
        #rain.append(1)
        ret = []
        counter = 0
        for month in ["Januari", "Februari", "Maart", "April", "Mei", "Juni", "Juli", "Augustus", "September", "Oktober", "November", "December"]:
            counter += 1
            ret.append({"label": month, "value": counter})
        return ret
    
    # Output("no-data-alert-bank", "style")
    @app.callback(
        [Output("bank-sample", "figure")],
        [Input("n-selection-slider", "value"), Input("bank-drop","value"), Input("time-window-slider", "value")],
    )
    def update_bank_sample_plot(n_value, dropdownValue, time_values):
        if time_values is None:
            return [{}]
        dataFrameSizePercentage = float(n_value / 100)
        local_df = dataFrameSize(KNMI_2000_Regen_df[KNMI_2000_Regen_df['Datum'].dt.month==dropdownValue], dataFrameSizePercentage)
        min_date, max_date = time_slider_to_date(time_values)
        values_sample, counts_sample = calculate_bank_sample_data(
            local_df, [min_date, max_date]
        )
    
        # Create a dictionary with the data
        data = {'Jaren': values_sample, 'Rain': counts_sample}
    
        # Create a pandas DataFrame from the dictionary
        df = pd.DataFrame(data)
    
        graph = px.bar(data_frame=df, x='Jaren', y='Rain', title='Regenval per maand' )
        layout = {
            "autosize": False,
            "margin": dict(t=10, b=10, l=40, r=0, pad=4),
            "xaxis": {"showticklabels": False},
        }
        return [ graph ]
    
    @app.callback(Output("bank-drop", "value"), [Input("bank-sample", "clickData")])
    def update_bank_drop_on_click(value):
        if value is not None:
            return value
        return ""
        
    return app.run(jupyter_mode="external"), output.serve_kernel_port_as_iframe(8050)
