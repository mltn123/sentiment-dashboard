from bs4 import BeautifulSoup
import bs4
import lxml
import feedparser
from textblob_de import TextBlobDE as TextBlob
from pandas.core.common import flatten
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
from datetime import datetime
import statistics
import openpyxl
from openpyxl import load_workbook
from flashtext import KeywordProcessor
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
import asyncio
import httpx
import time
import itertools
import cchardet
import gevent
import os
from bs4 import SoupStrainer
from waitress import serve
import urllib.parse as urlparse
import psycopg2
import plotly.express as px

app = dash.Dash(__name__)
server = app.server


url = urlparse.urlparse(os.environ['DATABASE_URL'])
dbname = url.path[1:]
user = url.username

password = url.password
host = url.hostname
port = url.port

con = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
            )
dbCursor = con.cursor()
sql = "select * from crawldata"



import time
#dbCursor.execute(sql)
data =  pd.read_sql_query(sql, con)
#data = pd.read_csv("dataclips.csv")
#data = pd.read_csv("MOCK_DATA.csv")

#print(data2)
#print(data2[0])
#data = pd.read_excel("Sentiments.xlsx")



data["date"] = pd.to_datetime(data["date"], format="%d/%m/%Y %H:%M:%S")
#data["date"] = pd.to_datetime(data["date"], format="%d/%m/%Y")

data.sort_values("date", inplace=True)
df_melt = data.melt(id_vars='date', value_vars=['sentimentcdu', 'sentimentgruene','sentimentspd',"sentimentfdp","sentimentafd"])
df_links = pd.DataFrame(data,columns=['date','linkscdu','linksgruene','linksspd','linksfdp','linksafd'])

app.layout = html.Div(
    html.Div([
        html.H4('Sentiment Analysis of several german news-sources towards largest political parties'),
        html.H6('News-Sources:'),
        html.Div(children=[
            html.Ul("https://www.spiegel.de/politik/index.rss"),
            html.Ul("https://www.tagesschau.de/xml/rss2/"),
            html.Ul("https://www.n-tv.de/politik/rss"),
            html.Ul("https://rss.sueddeutsche.de/rss/Politik"),
        ], ),

        dcc.Checklist(
                id='party_checklist',
                options=[
                    {'label': 'CDU/CSU', 'value': 'sentimentcdu'},
                    {'label': 'Gruene', 'value': 'sentimentgruene'},
                    {'label': 'SPD', 'value': 'sentimentspd'},
                    {'label': 'FDP', 'value': 'sentimentfdp'},
                    {'label': 'AFD', 'value': 'sentimentafd'},
                ],
                value=['sentimentcdu', 'sentimentgruene', 'sentimentspd', 'sentimentfdp', 'sentimentafd']
        ),
        dcc.Graph(id='line_graph'),
        dcc.Interval(
            id='interval_component',
            interval=1*300000, # in milliseconds
            n_intervals=0
        ),
        dash_table.DataTable(
            style_cell={
                'whiteSpace': 'normal',
                'height': 'auto',
                    },
            sort_action="native",
            editable=True,
            id='table',
            data=[],
            columns=[{"name": i, "id": i} for i in df_links.iloc[-10:]],
            # data=df_links.to_dict(),
        )
    ])
)

# @app.callback(
#     Output(component_id="line_graph", component_property='figure'),
#     [Input(component_id='party_checklist', component_property='value')],
# )
#
# def update_graph(options_chosen):
#     dff = df_melt[df_melt['variable'].isin(options_chosen)]
#     line_graph = px.line(dff, x="date", y="value")
#     return(line_graph)
#
# @app.callback(Output('line_graph', 'figure'),
#               Input('interval-component', 'n_intervals'))
# def update_graph_2(n):
#

@app.callback(
[Output('line_graph', 'figure'),Output('table', 'data')],
[Input('party_checklist', 'value'),Input('interval_component', 'n_intervals')])

def display(options_chosen,n):
    data =  pd.read_sql_query(sql, con)
    #data = pd.read_csv("dataclips.csv")
    data["date"] = pd.to_datetime(data["date"], format="%d/%m/%Y %H:%M:%S")
    data.sort_values("date", inplace=True)
    df_melt = data.melt(id_vars='date', value_vars=['sentimentcdu', 'sentimentgruene','sentimentspd',"sentimentfdp","sentimentafd"])
    df_links = pd.DataFrame(data,columns=['date','linkscdu','linksgruene','linksspd','linksfdp','linksafd'])
    df_links = df_links.iloc[-10:]
    ctx = dash.callback_context
    if ctx.triggered[0]:
        dff = df_melt[df_melt['variable'].isin(options_chosen)]
        line_graph = px.line(dff, x="date", y="value",color='variable', line_dash = 'variable')
        return(line_graph,df_links.to_dict('records'))
    if ctx.triggered[1]:
        dff = df_melt[df_melt['variable'].isin(options_chosen)]
        line_graph = px.line(dff, x="date", y="value",color='variable', line_dash = 'variable')
        return(line_graph,df_links.to_dict('records'))







#app.layout = serve_layout
if __name__ == '__main__':
    app.run_server(debug=True)
