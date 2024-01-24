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



def get_index_data(index, days):
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    df = index_df(symbol=index, from_date=start_date, to_date=end_date)
    p = figure(title= f"{index} closing prices", x_axis_label='Date', y_axis_label='Closing Price', x_axis_type='datetime' , width=500, height=300,toolbar_location=None)
    p.line(df['HistoricalDate'], df['CLOSE'], line_width=3)
    hover = HoverTool(
        tooltips=[
            ("Date", "@x{%F}"),
            ("Close", "@y"),
        ],
        formatters={
            '@x': 'datetime',  
        },
        mode='vline'
    )
    p.add_tools(hover)
    return p

   

def get_data(symbol_name, num_years):
    end_date = date.today()
    start_date = end_date - timedelta(days=365)
    # Fetch the data
    df_nifty = index_df(symbol="NIFTY 50", from_date=start_date, to_date=end_date)
    df_sensex = index_df(symbol="SENSEX", from_date=start_date, to_date=end_date)

    print(df_nifty.head())
    print(df_sensex.head())