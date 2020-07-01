import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import requests
from datetime import datetime

"""Request web service from esri"""
"""Web service returns data as JSON Format"""
"""Select data from features property and use it to build pandas dataframe"""
raw = requests.get("https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/Coronavirus_2019_nCoV_Cases/FeatureServer/1/query?where=1%3D1&outFields=*&outSR=4326&f=json")
raw_json = raw.json()
df = pd.DataFrame(raw_json["features"])

"""Data Transformation"""

data_list = df["attributes"].tolist()
df_final = pd.DataFrame(data_list)
df_final.set_index("OBJECTID")
df_final = df_final[["Country_Region", "Province_State", "Confirmed", "Deaths", "Recovered", "Last_Update"]]

"""Cleaning data"""

def convertTime(t):
    t = int(t)
    return datetime.fromtimestamp(t)

df_final = df_final.dropna(subset=["Last_Update"])
df_final["Province_State"].fillna(value="", inplace=True)

df_final["Last_Update"] = df_final["Last_Update"]/1000
df_final["Last_Update"] = df_final["Last_Update"].apply(convertTime)

"""Aggregating data"""

df_total = df_final.groupby("Country_Region", as_index=False).agg(
    {
        "Confirmed" : "sum",
        "Deaths" : "sum",
        "Recovered" : "sum"
    }
)

"""Calculating daily total at global level"""

total_confirmed = df_final["Confirmed"].sum()
total_recovered = df_final["Recovered"].sum()
total_deaths = df_final["Deaths"].sum()


"""Create subplot-Indicator"""

fig = make_subplots(
    rows=2, cols=3,

    specs=[
        [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
        [None, None, None]
    ]
)

fig.add_trace(
    go.Indicator(
        mode="number",
        value=total_confirmed,
        title="Confirmed Cases",
    ), row=1, col=1
)

fig.add_trace(
    go.Indicator(
        mode="number",
        value=total_recovered,
        title="Recovered Cases",
    ), row=1, col=2
)

fig.add_trace(
    go.Indicator(
        mode="number",
        value=total_deaths,
        title="Deaths Cases",
    ), row=1, col=3
)

fig.update_layout(
    template =  "plotly_dark",
    title = "GLOBAL COVID CASES (Last Updated: " + str(df_final["Last_Update"][0]) + ")"
)

fig.write_html("covid_figure.html", auto_open=True)