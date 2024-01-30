import plotly.graph_objects as go
import pandas as pd
from plotly.offline import plot
import stock_data as sd
import screen_reso as sr

nifty_50_stocks = sd.get_nifty50()

def get_plot(data_x, data_y, line_name, title, y_label, x_label, height=400, width=600):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data_x, y=data_y, mode="lines", name=line_name))

    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        autosize=False,
        width=width,
        height=height,
        xaxis=dict(showgrid=False),
        plot_bgcolor="rgb(230,230,230)",
        title_font=dict(size=25),
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
    return fig


def plot_stock_prices(
    symbol, y_parameter="Closing Price", x_parameter="Date", height=400, width=600
):
    data_x = sd.get_stock_historic_data(symbol, x_parameter)
    data_y = sd.get_stock_historic_data(symbol, y_parameter)

    dimensions = sr.get_screen_resolution()
    height = int(dimensions[1] * 0.46)
    width = int(dimensions[0] * 0.35)

    fig = get_plot(
        data_x,
        data_y,
        symbol,
        f"{symbol} {y_parameter}",
        y_parameter,
        x_parameter,
        height,
        width,
    )

    if sd.is_green(symbol):
        color = "green"
    else:
        color = "red"

    fig.update_traces(line_color=color)

    plot_div = plot(
        fig, output_type="div", include_plotlyjs=False, config={"displayModeBar": False}
    )
    return plot_div


def plot_index(
    index, y_parameter="Closing Price", x_parameter="Date", height=400, width=600
):
    data_y = sd.get_index_data(index, y_parameter)
    data_x = sd.get_index_data(index, x_parameter)

    dimensions = sr.get_screen_resolution()
    height = int(dimensions[1] * 0.46)
    width = int(dimensions[0] * 0.35)

    fig = get_plot(
        data_x,
        data_y,
        index,
        f"{index} {y_parameter}",
        y_parameter,
        x_parameter,
        height,
        width,
    )

    fig.update_traces(line_color="black")

    plot_div = plot(
        fig, output_type="div", include_plotlyjs=False, config={"displayModeBar": False}
    )
    return plot_div


def plot_and_compare_symbols(
    symbol_name_1, symbol_name_2, symbol_name_3, parameter, height=400, width=600
):
    if symbol_name_1 not in nifty_50_stocks or symbol_name_2 not in nifty_50_stocks:
        return None

    # dimensions = sr.get_screen_resolution()
    # height = int(dimensions[1] * 0.64)
    # width = int(dimensions[0] * 0.65)

    data_x = sd.get_stock_historic_data(symbol_name_1, "Date")
    data_y = sd.get_stock_historic_data(symbol_name_1, parameter)

    fig = get_plot(
        data_x,
        data_y,
        symbol_name_1,
        f"{symbol_name_1} {parameter}",
        parameter,
        "Date",
        height,
        width,
    )

    fig.add_trace(
        go.Scatter(
            x=sd.get_stock_historic_data(symbol_name_2, "Date"),
            y=sd.get_stock_historic_data(symbol_name_2, parameter),
            mode="lines",
            name=symbol_name_2,
        )
    )

    fig.update_layout(title=parameter)

    if symbol_name_3 in nifty_50_stocks:
        fig.add_trace(
            go.Scatter(
                x=sd.get_stock_historic_data(symbol_name_3, "Date"),
                y=sd.get_stock_historic_data(symbol_name_3, parameter),
                mode="lines",
                name=symbol_name_3,
            )
        )
    elif symbol_name_3 != "":
        return None

    plot_div = plot(
        fig,
        output_type="div",
        include_plotlyjs=False,
        config={"displayModeBar": False},
    )
    return plot_div
