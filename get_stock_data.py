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
    return df

def get_symbol_data(symbol, days):
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    df = stock_df(symbol=symbol, from_date=start_date, to_date=end_date)
    return df

def add_trace(fig, df, sym_name, xcolumn, ycolumn):
    fig.add_trace(go.Scatter(x=df[xcolumn], y=df[ycolumn], mode='lines', name=sym_name))
    fig.update_layout(title= "Closing Prices")
    return fig

def get_plot(df, sym_name, xcolumn, ycolumn):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[xcolumn], y=df[ycolumn], mode='lines', name=sym_name))

    fig.update_layout(title=f"{sym_name} closing prices", xaxis_title='Date', yaxis_title='Closing Price', autosize=False, width=700, height=400)
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
