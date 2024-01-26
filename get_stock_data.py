from jugaad_data.nse import index_df, stock_df
from jugaad_data.nse import NSELive
import sys
import time
import os
from datetime import date, timedelta
import plotly.graph_objects as go
import pandas as pd
from plotly.offline import plot

n=NSELive()

parameter_to_df_column = {
    "Closing Price": "CLOSE",
    "Opening Price": "OPEN",
    "High Price": "HIGH",
    "Low Price": "LOW",
    "Volume": "VOLUME",
    "Average Price": "VWAP",
    "Last Traded Price": "LTP",
    "Value": "VALUE",
    "Number of Trades": "NO OF TRADES",
}
nifty_50 = list(pd.read_csv("ind_nifty50list.csv")["Symbol"])

def get_nifty50():
    return nifty_50

def get_stock_compare_parameters():
    return [
        "Closing Price",
        "Opening Price",
        "High Price",
        "Low Price",
        "Volume",
        "Average Price",
    ]

def get_live_symbol_data(symbol):
    query=n.stock_quote(symbol)
    return query['priceInfo']
    
def get_index_data(index, days):
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    df = index_df(symbol=index, from_date=start_date, to_date=end_date)
    df.drop_duplicates(subset=["HistoricalDate"], inplace=True)
    return df

def get_symbol_data(symbol, days):
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    df = stock_df(symbol=symbol, from_date=start_date, to_date=end_date)
    return df

# def add_trace(fig, df, sym_name, xcolumn, ycolumn, title):
#     fig.add_trace(go.Scatter(x=df[xcolumn], y=df[ycolumn], mode="lines", name=sym_name))
#     fig.update_layout(title=title)
#     return fig

def get_plot(df, sym_name, xcolumn, ycolumn, title, height, width):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[xcolumn], y=df[ycolumn], mode="lines", name=sym_name))

    fig.update_layout(
        title=f"{sym_name} {title}",
        xaxis_title="Date",
        yaxis_title=title,
        autosize=False,
        width=width,
        height=height,
    )
    fig.update_xaxes(
        rangeslider_visible=False,
        rangeselector=dict(
            buttons=list(
                [
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(label="2Y", step="all"),
                ]
            )
        ),
    )
    fig.update_yaxes(autorange=True, scaleanchor="x", scaleratio=1)
    fig.update_yaxes(range=[min(df[ycolumn]), max(df[ycolumn])])
    return fig

def plot_symbol(symbol, parameter, height=500, width=1000):
    num_years = 2
    days = 365 * num_years
    ycolumn=  parameter_to_df_column[parameter]
    fig = get_plot(
        get_symbol_data(symbol, days), symbol, 'DATE', ycolumn, parameter,height,width
    )
    plot_div = plot(
        fig, output_type="div", include_plotlyjs=False, config={"displayModeBar": False}
    )
    return plot_div

def plot_index(height=500, width=1000):
    num_years = 2
    days = 365 * num_years
    fig = get_plot(
        get_index_data("NIFTY 50", days), "NIFTY 50", "HistoricalDate", "CLOSE", 'Closing Prices',height,width
    )
    plot_div = plot(
        fig, output_type="div", include_plotlyjs=False, config={"displayModeBar": False}
    )
    return plot_div

def plot_and_compare_symbols(symbol_name_1, symbol_name_2, symbol_name_3, parameter, height=500, width=1000):
    if symbol_name_1 not in nifty_50 or symbol_name_2 not in nifty_50:
        return None
    num_years = 2
    days = 365 * num_years
    ycol = parameter_to_df_column[parameter]
    fig = get_plot(
        get_symbol_data(symbol_name_1, days), symbol_name_1, "DATE", ycol, parameter,height,width
    )
    df = get_symbol_data(symbol_name_2, days)
    fig.add_trace(go.Scatter(x=df['DATE'], y=df[ycol], mode="lines", name=symbol_name_2))
    fig.update_layout(title=parameter)
    if symbol_name_3 in nifty_50:
        df = get_symbol_data(symbol_name_3, days)
        fig.add_trace(go.Scatter(x=df['DATE'], y=df[ycol], mode="lines", name=symbol_name_3))
    plot_div = plot(
        fig,
        output_type="div",
        include_plotlyjs=False,
        config={"displayModeBar": False},
    )
    return plot_div

# stock_symbols = ['DRREDDY','EICHERMOT','GRASIM','HCLTECH','ADANIENT','ADANIPORTS','APOLLOHOSP','ASIANPAINT','AXISBANK']  # Add all your 50 stock symbols here
# ascending_data = []
# stockdata={}
# for symbol in stock_symbols:
#     stockdata[symbol]=get_live_symbol_data(symbol)
#     ascending_data.append({'symbol':symbol,'pchange':stockdata[symbol]['pChange'],'price':stockdata[symbol]['lastPrice']})  
# ascending_data = sorted(ascending_data, key=lambda x: x['pchange'])
# print(ascending_data)