from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool
from bokeh.resources import CDN
from jugaad_data.nse import index_df
import sys
from datetime import date, timedelta
from jugaad_data.nse import stock_df
import time
import os
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go



def get_index_data(index, days):
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    df = index_df(symbol=index, from_date=start_date, to_date=end_date)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['HistoricalDate'], y=df['CLOSE'], mode='lines', name=index))

    fig.update_layout(title=f"{index} closing prices", xaxis_title='Date', yaxis_title='Closing Price', autosize=False, width=700, height=400)
    fig.update_xaxes(
    rangeslider_visible=False,
    rangeselector=dict(
        buttons=list([
            dict(count=1, label="1M", step="month", stepmode="backward"),
            dict(count=6, label="6M", step="month", stepmode="backward"),
            dict(count=1, label="1Y", step="year", stepmode="backward"),
            dict(label= "2Y",step="all")
        ])
    ))
    fig.update_yaxes(autorange=True, scaleanchor="x", scaleratio=1)
    fig.update_yaxes(range=[min(df['CLOSE']), max(df['CLOSE'])]) 
    
    return fig

def get_data(symbol_name, num_years):
    end_date = date.today()
    start_date = end_date - timedelta(days=365)
    # Fetch the data
    df_nifty = index_df(symbol="NIFTY 50", from_date=start_date, to_date=end_date)
    df_sensex = index_df(symbol="SENSEX", from_date=start_date, to_date=end_date)

    print(df_nifty.head())
    print(df_sensex.head())