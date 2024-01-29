from jugaad_data.nse import index_df, stock_df
from jugaad_data.nse import NSELive
from datetime import date, timedelta
import pandas as pd
from bsedata.bse import BSE

# Declare global variables
b = BSE()
n = NSELive()
indices = ["NIFTY 50"]
nifty_50_stocks = list(pd.read_csv("ind_nifty50list.csv")["Symbol"])
base_years = 2

# Fetch Live Index Data while starting the server
index_live_data = {}
sensex_data_raw = b.getIndices(category="market_cap/broad")["indices"][0]
index_live_data["SENSEX"] = {
    "pchange": float(sensex_data_raw["pChange"]),
    "price": sensex_data_raw["currentValue"],
}

nifty_data_raw = n.live_index("NIFTY 50")["data"][0]
index_live_data["NIFTY 50"] = {
    "pchange": nifty_data_raw["pChange"],
    "price": nifty_data_raw["lastPrice"],
}

# Store Historic index data
index_historic_data = {}
for index in indices:
    end_date = date.today()
    start_date = end_date - timedelta(days=base_years * 365)
    df = index_df(symbol=index, from_date=start_date, to_date=end_date)
    df.drop_duplicates(subset=["HistoricalDate"], inplace=True)
    index_historic_data[index] = df

# Private datastructures and functions to store some mappings
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
    "Percent Change": "PCHANGE",
}

index_parameter_to_df_column = {"Closing Price": "CLOSE", "Date": "HistoricalDate"}


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
    "52 Week Low",
]


def get_today_stock_data(symbol, parameter):
    if symbol not in stock_curr_data.keys():
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        df = stock_df(symbol=symbol, from_date=start_date, to_date=end_date)
        df["PCHANGE"] = (df["LTP"] / df["PREV. CLOSE"]) * 100 - 100
        stock_curr_data[symbol] = df.iloc[0]
    return stock_curr_data[symbol][stock_parameter_to_df_column[parameter]]


# Initiate today's stock data
stock_historic_data = {}
stock_curr_data = {}


def get_nifty50():
    return nifty_50_stocks


def get_stock_compare_parameters():
    return [
        "Closing Price",
        "Opening Price",
        "Average Price",
        "Volume",
        "Value",
        "Number of Trades",
    ]


def get_stock_filter_parameters():
    return [
        "Closing Price",
        "Average Price",
        "Volume",
        "Last Traded Price",
    ]


def get_live_index_data(index):
    return index_live_data[index]


def get_index_data(index, parameter):
    return index_historic_data[index][index_parameter_to_df_column[parameter]]


def is_green(symbol):
    return stock_curr_data[symbol]["PCHANGE"] >= 0


def get_stock_historic_data(symbol, parameter):
    if symbol not in stock_historic_data.keys():
        end_date = date.today()
        start_date = end_date - timedelta(days=365 * base_years)
        df = stock_df(symbol=symbol, from_date=start_date, to_date=end_date)
        stock_historic_data[symbol] = df
    return stock_historic_data[symbol][stock_parameter_to_df_column[parameter]]


def get_stock_card(symbol):
    return {
        "symbol": symbol,
        "pchange": get_today_stock_data(symbol, "Percent Change"),
        "price": get_today_stock_data(symbol, "Last Traded Price"),
    }


def get_all_stock_cards(lt=1e10, gt=-1e10, parameter=""):
    stock_card_data = []
    for stock in nifty_50_stocks:
        if (
            parameter == ""
            or get_today_stock_data(stock, parameter) <= lt
            and get_today_stock_data(stock, parameter) >= gt
        ):
            stock_card_data.append(get_stock_card(stock))
    return stock_card_data


def get_stock_page_data(symbol):
    detail_data = {}
    for parameter in stock_parameter_to_display:
        detail_data[parameter] = get_today_stock_data(symbol, parameter)
    return detail_data
