from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from jugaad_data.nse import stock_df
from datetime import date, timedelta
import pandas as pd
import get_stock_data as gsd
import news as n

nifty_50_stocks = list(pd.read_csv("ind_nifty50list.csv")["Symbol"])
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with your actual secret key

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)


# Initialize Database within Application Context
with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password,
                                                 method="pbkdf2:sha256")

        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.")
        return redirect(url_for("index"))
    return render_template("register.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        session["user_id"] = user.id
        session["username"] = user.username
        return redirect(url_for("dashboard"))
    else:
        flash("Invalid username or password")
        return redirect(url_for("index"))


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'user_id' in session:
        form_posted=False
        nifty_50_stocks = gsd.get_nifty50()
        plot_div = gsd.plot_index('NIFTY 50', width=750, height=460)
        stocks_data = gsd.get_all_stock_card_data()

        ascending_data = sorted(stocks_data, key=lambda x: x['pchange'])
        descending_data = ascending_data[::-1]
        search_error = ""
        filter_error = ""
        if request.method == 'POST':
            form_posted=True
            form_type = request.form.get('form_type')
            if form_type == 'search':
                symbol_entered = request.form.get('search').upper()
                if symbol_entered in nifty_50_stocks:
                    return redirect(url_for('stock', symbol=symbol_entered))
                else:
                    search_error = "Wrong symbol entered"
            elif form_type == 'filter':
                less_than = request.form.get("less")
                greater_than = request.form.get("greater")
                parameter = request.form.get("stock_parameter")
                try:
                    if less_than == "":
                        lt = 1e10
                    else:
                        lt = float(less_than)

                    if greater_than == "":
                        gt = -1e10
                    else:
                        gt = float(greater_than)
                except:
                    filter_error = "Please enter valid values"
                else:
                    stocks_data = gsd.get_all_stock_card_data(
                        lt, gt, parameter)

                    return render_template(
                        'dashboard.html',
                        username=session['username'],
                        stocks_data=stocks_data,
                        dsc=descending_data[:5],
                        asc=ascending_data[:5],
                        plot_div=plot_div,
                        news_articles=n.get_news()['articles'][:4],
                        nifty50_data=gsd.get_live_index_data("NIFTY 50"),
                        sensex_data=gsd.get_live_index_data("SENSEX"),
                        parameter_options=gsd.get_stock_filter_parameters(),
                        search_error=search_error,
                        filter_error=filter_error,
                        form_posted=form_posted,)
        return render_template(
            'dashboard.html',
            username=session['username'],
            stocks_data=stocks_data,
            dsc=descending_data[:5],
            asc=ascending_data[:5],
            plot_div=plot_div,
            news_articles=n.get_news()['articles'][:4],
            nifty50_data=gsd.get_live_index_data("NIFTY 50"),
            sensex_data=gsd.get_live_index_data("SENSEX"),
            parameter_options=gsd.get_stock_filter_parameters(),
            search_error=search_error,
            filter_error=filter_error,
            form_posted=form_posted,)

    else:
        return redirect(url_for('index'))


@app.route('/stock/<symbol>')
def stock(symbol):
    stock_card_data = gsd.get_stock_card_data(symbol)
    stock_detail_data = gsd.get_stock_detail_data(symbol)
    plot_div = gsd.plot_stock_prices(symbol, 400, 500)
    return render_template(
        'stockdata.html',
        stock_card_data=stock_card_data,  #dictionary with symbol,
        stock_detail_data=stock_detail_data,
        plot_div=plot_div,
        nifty50_data=gsd.get_live_index_data("NIFTY 50"),
        sensex_data=gsd.get_live_index_data("SENSEX"),
        news_articles=n.get_news()['articles'][:4])

@app.route("/stonks")
def stonks():
    return render_template('stonks.html')


@app.route("/plot_compare", methods=["GET", "POST"])
def plot_compare():
    parameter_options = gsd.get_stock_compare_parameters()
    if request.method == "POST":
        symbol_name_1 = request.form.get("stock1")
        symbol_name_2 = request.form.get("stock2")
        symbol_name_3 = request.form.get("stock3")
        parameter = request.form.get("stock_parameter")

        plot_div = gsd.plot_and_compare_symbols(symbol_name_1, symbol_name_2,
                                                symbol_name_3, parameter, 600,
                                                1000)
        if plot_div is None:
            return render_template(
                "plot_compare.html",
                parameter_options=parameter_options,
                error="Please enter valid stock symbols",
                news_articles=n.get_news()['articles'][:4],
                nifty50_data=gsd.get_live_index_data("NIFTY 50"),
                sensex_data=gsd.get_live_index_data("SENSEX"),
            )

        return render_template(
            "plot_compare.html",
            plot_div=plot_div,
            stock1=symbol_name_1,
            stock2=symbol_name_2,
            stock3=symbol_name_3,
            parameter_options=parameter_options,
            news_articles=n.get_news()['articles'][:4],
            nifty50_data=gsd.get_live_index_data("NIFTY 50"),
            sensex_data=gsd.get_live_index_data("SENSEX"),
        )
    return render_template("plot_compare.html",
                           parameter_options=parameter_options,
                           news_articles=n.get_news()['articles'][:4],
                           nifty50_data=gsd.get_live_index_data("NIFTY 50"),
                           sensex_data=gsd.get_live_index_data("SENSEX"))


@app.route("/reset_filter")
def reset_filter():
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
