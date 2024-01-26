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

b = BSE()
n = NSELive()
indices = ["NIFTY 50"]
nifty_50_stocks = list(pd.read_csv("ind_nifty50list.csv")["Symbol"])
base_years = 2

# Fetch Live Index Data while starting the server
index_live_data = {}
index_live_data["SENSEX"] = b.getIndices(category="market_cap/broad")["indices"][0]
index_live_data['SENSEX']['pChange']=float(index_live_data['SENSEX']['pChange'])
index_live_data["NIFTY 50"] = n.live_index("NIFTY 50")["data"][0]

# Store Historic index data
index_historic_data = {}
for index in indices:
    end_date = date.today()
    start_date = end_date - timedelta(days=base_years * 365)
    df = index_df(symbol=index, from_date=start_date, to_date=end_date)
    df.drop_duplicates(subset=["HistoricalDate"], inplace=True)
    index_historic_data[index] = df

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


def get_nifty50():
    return nifty_50_stocks


def get_stock_compare_parameters():
    return [
        "Closing Price",
        "Opening Price",
        "High Price",
        "Low Price",
        "Volume",
        "Average Price",
    ]


def get_stock_display_parameters():
    return {
        "CLOSE": "Closing Price",
        "OPEN": "Opening Price",
        "HIGH": "High Price",
        "LOW": "Low Price",
        "VOLUME": "Volume",
        "VWAP": "Average Price",
        "VALUE": "Value",
        "PREV. CLOSE": "Previous Close",
        "52W H": "52 Week High",
        "52W L": "52 Week Low",
    }


def get_live_symbol_data(symbol):
    query = n.stock_quote(symbol)
    return query["priceInfo"]


def get_live_index_data(index):
    return index_live_data[index]


def get_index_data(index):
    return index_historic_data[index]


def get_symbol_data(symbol, days=2 * 365):
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    df = stock_df(symbol=symbol, from_date=start_date, to_date=end_date)
    return df


def get_plot(df, sym_name, xcolumn, ycolumn, title, height=400, width=600):
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
    fig.update_layout(xaxis=dict(showgrid=False), plot_bgcolor="rgb(230,230,230)")
    fig.update_layout(
    title_font=dict(size=25))
    return fig


def plot_symbol(symbol, parameter, height=500, width=1000):
    days = 365 * base_years
    df = get_symbol_data(symbol, days)
    ycolumn = parameter_to_df_column[parameter]
    fig = get_plot(df, symbol, "DATE", ycolumn, parameter, height, width)
    if df[ycolumn].iloc[0] > df[ycolumn].iloc[1]:
        fig.update_traces(line_color="green")
    else:
        fig.update_traces(line_color="red")
    
    plot_div = plot(
        fig, output_type="div", include_plotlyjs=False, config={"displayModeBar": False}
    )
    return plot_div


def plot_index(index, height=500, width=1000):
    days = 365 * base_years
    fig = get_plot(
        index_historic_data[index],
        index,
        "HistoricalDate",
        "CLOSE",
        "Closing Prices",
        height,
        width,
    )
    fig.update_traces(line_color="green")
    
    plot_div = plot(
        fig, output_type="div", include_plotlyjs=False, config={"displayModeBar": False}
    )
    return plot_div


def plot_and_compare_symbols(
    symbol_name_1, symbol_name_2, symbol_name_3, parameter, height=500, width=1000
):
    if symbol_name_1 not in nifty_50_stocks or symbol_name_2 not in nifty_50_stocks:
        return None
    days = 365 * base_years
    ycol = parameter_to_df_column[parameter]
    fig = get_plot(
        get_symbol_data(symbol_name_1, days),
        symbol_name_1,
        "DATE",
        ycol,
        parameter,
        height,
        width,
    )
    df = get_symbol_data(symbol_name_2, days)
    fig.add_trace(
        go.Scatter(x=df["DATE"], y=df[ycol], mode="lines", name=symbol_name_2)
    )
    fig.update_layout(title=parameter)
    if symbol_name_3 in nifty_50_stocks:
        df = get_symbol_data(symbol_name_3, days)
        fig.add_trace(
            go.Scatter(x=df["DATE"], y=df[ycol], mode="lines", name=symbol_name_3)
        )
    plot_div = plot(
        fig,
        output_type="div",
        include_plotlyjs=False,
        config={"displayModeBar": False},
    )
    return plot_div


# print(get_symbol_data('RELIANCE', 1))
