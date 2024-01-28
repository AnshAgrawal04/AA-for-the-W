from jugaad_data.nse import index_df, stock_df
from jugaad_data.nse import NSELive
import sys
import time
import os
from datetime import date, timedelta
import plotly.graph_objects as go
import pandas as pd
from plotly.offline import plot
from bsedata.bse import BSE
import screen_reso as sr


b = BSE()
n = NSELive()
indices = ["NIFTY 50"]
nifty_50_stocks = list(pd.read_csv("ind_nifty50list.csv")["Symbol"])
base_years = 2

# Fetch Live Index Data while starting the server
index_live_data = {}
index_live_data["SENSEX"] = b.getIndices(
    category="market_cap/broad")["indices"][0]
index_live_data["SENSEX"]["pChange"] = float(
    index_live_data["SENSEX"]["pChange"])
index_live_data["NIFTY 50"] = n.live_index("NIFTY 50")["data"][0]

# Store Historic index data
index_historic_data = {}
for index in indices:
    end_date = date.today()
    start_date = end_date - timedelta(days=base_years * 365)
    df = index_df(symbol=index, from_date=start_date, to_date=end_date)
    df.drop_duplicates(subset=["HistoricalDate"], inplace=True)
    index_historic_data[index] = df

stock_parameter_to_df_column = {
    "Closing Price": "CLOSE",
    "Opening Price": "OPEN",
    "High Price": "HIGH",
    "Low Price": "LOW",
    "Volume": "VOLUME",
    "Average Price": "VWAP",
    "Last Traded Price": "LTP",
    "Value": "VALUE",
    "Number of Trades": "NO OF TRADES",
    "Previous Close": "PREV. CLOSE",
    "52 Week High": "52W H",
    "52 Week Low": "52W L",
    "Date": "DATE", 
    "Percent Change": "PCHANGE"
}

 
stock_parameter_to_display = [
    "Closing Price",
    "Opening Price",
    "High Price",
    "Low Price",
    "Volume",
    "Average Price",
    "Value",
    "Number of Trades",
    "Previous Close",
    "52 Week High",
    "52 Week Low"
]

#Initiate today's stock data
stock_historic_data = {}
stock_curr_data = {}

def get_nifty50():
    return nifty_50_stocks

def get_stock_compare_parameters():
    return [
        "Closing Price",
        "Opening Price",
        "Average Price",
        "Volume"
    ]

def get_stock_filter_parameters():
    return[
        'High Price',
        'Low Price',
        'Volume',
        'Last Traded Price',
    ]

def get_live_index_data(index):
    return index_live_data[index]

def get_index_data(index):
    return index_historic_data[index]

def get_stock_historic_data(symbol, parameter):
    if symbol not in stock_historic_data.keys():
        end_date = date.today()
        start_date = end_date - timedelta(days=365 * base_years)
        df = stock_df(symbol=symbol, from_date=start_date, to_date=end_date)
        stock_historic_data[symbol] = df
    return stock_historic_data[symbol][stock_parameter_to_df_column[parameter]]

def get_all_stock_card_data(lt=1e10, gt=-1e10, parameter=""):
    stock_card_data = []
    for stock in nifty_50_stocks:
        if parameter=="" or get_stock_curr_data(stock, parameter) <= lt and get_stock_curr_data(stock, parameter) >= gt:
            stock_card_data.append(get_stock_card_data(stock))
    return stock_card_data

def get_stock_curr_data(symbol, parameter):
    if symbol not in stock_curr_data.keys():
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        df = stock_df(symbol=symbol, from_date=start_date, to_date=end_date)
        df['PCHANGE'] = (df['LTP'] / df['PREV. CLOSE'])* 100 - 100
        stock_curr_data[symbol] = df.iloc[0]
    return stock_curr_data[symbol][stock_parameter_to_df_column[parameter]]

def is_green(symbol):
    return stock_curr_data[symbol]['PCHANGE'] >= 0

def get_stock_card_data(symbol):
    return {
        "symbol": symbol,
        "pchange": get_stock_curr_data(symbol, 'Percent Change'),
        "price": get_stock_curr_data(symbol, 'Last Traded Price'), 
    }

def get_stock_detail_data(symbol):
    detail_data={}
    for parameter in stock_parameter_to_display:
        detail_data[parameter] = get_stock_curr_data(symbol, parameter)
    return detail_data


def get_plot(data_x,
             data_y,
             line_name,
             title,
             y_label,
             x_label,
             height=400,
             width=600):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data_x, y=data_y, mode="lines", name=line_name))

    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        autosize=False,
        width=width,
        height=height,
    )
    fig.update_xaxes(
        rangeslider_visible=False,
        rangeselector=dict(buttons=list([
            dict(count=1, label="1M", step="month", stepmode="backward"),
            dict(count=6, label="6M", step="month", stepmode="backward"),
            dict(count=1, label="1Y", step="year", stepmode="backward"),
            dict(label="2Y", step="all"),
        ])),
    )
    fig.update_yaxes(autorange=True, scaleanchor="x", scaleratio=1)
    fig.update_yaxes(range=[min(data_y), max(data_y)])
    fig.update_layout(xaxis=dict(showgrid=False),
                      plot_bgcolor="rgb(230,230,230)")
    fig.update_layout(title_font=dict(size=25))
    return fig

def plot_stock_prices(symbol, height=400, width=600):
    days = 365 * base_years
    data_x = get_stock_historic_data(symbol, 'Date')
    data_y = get_stock_historic_data(symbol, 'Closing Price')

    dimensions = sr.get_screen_resolution()
    height = int(dimensions[1] * 0.46)
    width = int(dimensions[0] * 0.35)

    fig = get_plot(data_x, data_y, symbol, f"{symbol} Prices", "Prices",
                   "Date", height, width)

    if is_green(symbol):
        fig.update_traces(line_color="green")
    else:
        fig.update_traces(line_color="red")

    plot_div = plot(fig,
                    output_type="div",
                    include_plotlyjs=False,
                    config={"displayModeBar": False})
    return plot_div

def plot_index(index, height=400, width=600):
    days = 365 * base_years
    df = get_index_data(index)

    dimensions = sr.get_screen_resolution()
    height = int(dimensions[1] * 0.46)
    width = int(dimensions[0] * 0.35)

    fig = get_plot(df['HistoricalDate'], df['CLOSE'], index,
                   f"{index} Closing Prices", "Prices", "Date", height, width)

    fig.update_traces(line_color="black")

    plot_div = plot(fig,
                    output_type="div",
                    include_plotlyjs=False,
                    config={"displayModeBar": False})
    return plot_div

def plot_and_compare_symbols(symbol_name_1,
                             symbol_name_2,
                             symbol_name_3,
                             parameter,
                             height=400,
                             width=600):
    if symbol_name_1 not in nifty_50_stocks or symbol_name_2 not in nifty_50_stocks:
        return None
    days = 365 * base_years

    dimensions = sr.get_screen_resolution()
    height = int(dimensions[1] * 0.64)
    width = int(dimensions[0] * 0.65)

    data_x = get_stock_historic_data(symbol_name_1, 'Date')
    data_y = get_stock_historic_data(symbol_name_1, parameter)

    fig = get_plot(data_x, data_y, symbol_name_1, f"{symbol_name_1} {parameter}", parameter,
                   "Date", height, width)

    data_x = get_stock_historic_data(symbol_name_2, 'Date')
    data_y = get_stock_historic_data(symbol_name_2, parameter)

    fig.add_trace(
        go.Scatter(x=data_x, y=data_y, mode="lines", name=symbol_name_2))

    fig.update_layout(title=parameter)

    if symbol_name_3 in nifty_50_stocks:
        data_x = get_stock_historic_data(symbol_name_3, 'Date')
        data_y = get_stock_historic_data(symbol_name_3, parameter)
        fig.add_trace(
            go.Scatter(x=data_x, y=data_y, mode="lines", name=symbol_name_3))

    plot_div = plot(
        fig,
        output_type="div",
        include_plotlyjs=False,
        config={"displayModeBar": False},
    )
    return plot_div
