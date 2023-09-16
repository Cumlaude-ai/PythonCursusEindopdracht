import pathlib
import re
import json
from datetime import datetime
import flask
import dash
import dash_table
import matplotlib.colors as mcolors
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input, State
import random
from google.colab import output
from dateutil import relativedelta


# Create a list of years from 2000 to 2023
years = list(range(2000, 2024))

# Create a dictionary with the data
data = {'Jaren': years, 'Rain': [0] * len(years)}

# Create a pandas DataFrame from the dictionary
emptyDataframe = pd.DataFrame(data)

emptyGraph = px.bar(data_frame=emptyDataframe,x='Jaren', y='Rain', title='Regenval per maand')

maanden = ['Jan', 'Feb', 'Mrt', 'Apr', 'Mei', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']
jaren = list(range(2022, 2024))
waterstand_data = []

for jaar in jaren:
    for maand in maanden:
        waterstand_data.append({
            'Jaar': jaar,
            'Maand': maand,
            'Waterstand (cm)': random.uniform(0, 200)
        })

# Creëer een DataFrame van de gegenereerde gegevens
df = pd.DataFrame(waterstand_data)

# Creëer een lijngrafiek met Plotly Express
waterstand_fig = px.line(df, x='Maand', y='Waterstand (cm)', color='Jaar',
              title='Maandelijkse Waterstanden Over de Jaren',
              labels={'Waterstand (cm)': 'Waterstand (cm)', 'Jaar': 'Jaar'})

#Real data
KNMI_df = pd.read_csv("https://raw.githubusercontent.com/Cumlaude-ai/Python_Cursus/main/data/KNMI_De_Bilt.csv", skiprows=51, skipinitialspace = True )

KNMI_df.columns = ["STN","Datum","Vectorgemiddelde windrichting","Vectorgemiddelde windsnelheid","Etmaalgemiddelde windsnelheid","Hoogste uurgemiddelde windsnelheid","Uurvak FHX","Laagste uurgemiddelde windsnelheid","Uurvak FHN","Hoogste windstoot","Uurvak FXX","Etmaalgemiddelde temperatuur","Minimum temperatuur",'Uurvak TN',"Maximum temperatuur","Uurvak TX","Minimum temperatuur op 10 cm","6-Uurs minimum temperatuur","Zonneschijnduur","Percentage maximale zonneschijnduur","Globale straling","Duur van de neerslag","Etmaalsom neerslag","Hoogste uursom neerslag","Uurvak RHX","Etmaalgemiddelde luchtdruk","Hoogste uurwaarde luchtdruk","Uurvak PX","Laagste uurwaarde luchtdruk","Uurvak PN","Minimum zicht","Uurvak VVN","Maximum zicht","Uurvak VVX","Etmaalgemiddelde bewolking","Etmaalgemiddelde vochtigheid","Maximale vochtigheid","Uurvak UX","Minimale vochtigheid","Uurvak UN","Referentiegewasverdamping"]

KNMI_df = KNMI_df.dropna(subset=['Etmaalsom neerslag'])

# De datum van YYYY-MM-DD format naar een pandas datetime format
KNMI_df['Datum'] = pd.to_datetime(KNMI_df['Datum'], format='%Y%m%d')

# Selecteer alleen data groter dan het jaar 2000
KNMI_2000_df = KNMI_df[KNMI_df['Datum'] >= '2000-01-01']

# Vervang metingen met -1 (minder dan 0,05 mm) met 0
KNMI_2000_Regen_df = KNMI_2000_df[["Datum","Etmaalsom neerslag","Hoogste uursom neerslag"]].replace("   -1",0)

KNMI_2000_Regen_df.index = pd.to_datetime(KNMI_2000_Regen_df['Datum'], format='%Y%m%d')

#Grouped_KNMI = KNMI_2000_Regen_df.groupby(KNMI_2000_Regen_df.index.month)

#Grouped_KNMI["Hoogste uursom neerslag"].mean().count()
def createDashboard():
    NAVBAR = dbc.Navbar(
        children=[
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src="https://github.com/Cumlaude-ai/Python_Cursus/blob/main/data/WetterskipLogoTransparent.png?raw=true", height="50px")),
                        dbc.Col(
                            dbc.NavbarBrand("Wetterskip dashboard", className="ml-2")
                        ),
                    ],
                    align="center",
                ),
                href="https://www.wetterskipfryslan.nl",
                style={"text-decoration": "none"},
            )
        ],
        color="dark",
        dark=True,
        sticky="top",
        style={"background-size":"cover","color":"white","background-image":"url('https://www.wetterskipfryslan.nl/afbeeldingen/headerfotos/headerfoto-zomer-zeedijk-schiermonnikoog-2.png')"},
    )
    # Customization menu
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
    
    WORDCLOUD_PLOTS = [
        dbc.CardHeader(html.H5("Waterstanden")),
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
                              dcc.Graph(id="bank-treemap",figure=waterstand_fig)
                              ],
                          type="default",
                        ),
                    ]
                )
            ]
        ),
    ]
    
    TOP_BANKS_PLOT = [
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
    
    BODY = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(LEFT_COLUMN, md=4, align="center"),
                    dbc.Col(dbc.Card(TOP_BANKS_PLOT), md=8),
                ],
                style={"marginTop": 30},
            ),
            dbc.Card(WORDCLOUD_PLOTS),
        ],
        className="mt-12",
    )
    
    
    
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout = html.Div(children=[NAVBAR, BODY])
    
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
        
    return app.run(jupyter_mode="external")
