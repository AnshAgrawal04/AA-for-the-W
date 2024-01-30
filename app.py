from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    session,
)

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from jugaad_data.nse import stock_df
from datetime import date, timedelta
import pandas as pd
import stock_data as sd
import stock_plots as sp
import news as n

nifty_50_stocks = list(pd.read_csv("ind_nifty50list.csv")["Symbol"])
news_articles = n.get_news()["articles"][:4]
sensex_data = sd.get_live_index_data("SENSEX")
nifty50_data = sd.get_live_index_data("NIFTY 50")

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
    watchlist = db.relationship("Watchlist", backref="user", lazy=True)

class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    symbol1 = db.Column(db.String(100))
    symbol2 = db.Column(db.String(100))
    symbol3 = db.Column(db.String(100))
    symbol4 = db.Column(db.String(100))

# Initialize Database within Application Context
with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    iframe='/static/nav-bar.html',
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.")
        return redirect(url_for("index"))
    return render_template("register.html",iframe=iframe)


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
        return redirect(url_for("index"),iframe='/static/nav-bar.html')


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("index"))
        
    plot_div = sp.plot_index("NIFTY 50", width=750, height=460)
    stocks_data = sd.get_all_stock_cards()
    ascending_data = sorted(stocks_data, key=lambda x: x["pchange"])
    descending_data = ascending_data[::-1]

    search_error, filter_error, form_posted = "", "", False

    if request.method == "POST":
        form_posted = True
        form_type = request.form.get("form_type")
        if form_type == "search":
            symbol_entered = request.form.get("search").upper()
            if symbol_entered in sd.get_nifty50():
                return redirect(url_for("stock", symbol=symbol_entered))
            search_error = "Wrong symbol entered"
        elif form_type == "filter":
            less_than = request.form.get("less")
            greater_than = request.form.get("greater")
            parameter = request.form.get("stock_parameter")

            try:
                lt = float(less_than) if less_than else 1e10
                gt = float(greater_than) if greater_than else -1e10
            except:
                filter_error = "Please enter valid values"
                form_posted = False
            else:
                stocks_data = sd.get_all_stock_cards(lt, gt, parameter)

    return render_template(
        "dashboard.html",
        username=session["username"],
        stocks_data=stocks_data,
        dsc=descending_data[:5],
        asc=ascending_data[:5],
        plot_div=plot_div,
        news_articles=news_articles,
        nifty50_data=nifty50_data,
        sensex_data=sensex_data,
        parameter_options=sd.get_stock_filter_parameters(),
        search_error=search_error,
        filter_error=filter_error,
        form_posted=form_posted,
    )

@app.route("/stock/<symbol>",methods=["GET","POST"])
def stock(symbol):
    user = User.query.filter_by(username=session['username']).first()
    
    stock_card_data = sd.get_stock_card(symbol)
    stock_detail_data = sd.get_stock_page_data(symbol)
    plot_div = sp.plot_stock_prices(symbol, height=400, width=500)
    if request.method == "POST":
        
        if not user.watchlist:
            
            watchlist = Watchlist(user_id=user.id,symbol1=symbol)
            db.session.add(watchlist)
            db.session.commit()
        else:
            watchlist = user.watchlist[0]
            if not watchlist.symbol1:
                watchlist.symbol1 = symbol
            elif not watchlist.symbol2:
                watchlist.symbol2 = symbol
            elif not watchlist.symbol3:
                watchlist.symbol3 = symbol
            elif not watchlist.symbol4:
                watchlist.symbol4 = symbol
            elif watchlist.symbol1 != symbol and watchlist.symbol2 != symbol and watchlist.symbol3 != symbol and watchlist.symbol4 != symbol:
                watchlist.symbol1 = watchlist.symbol2
                watchlist.symbol2 = watchlist.symbol3
                watchlist.symbol3 = watchlist.symbol4
                watchlist.symbol4 = symbol
            db.session.commit()
    local_watchlist = []
    if user.watchlist:
        if user.watchlist[0].symbol1:
            local_watchlist.append(user.watchlist[0].symbol1)
        if user.watchlist[0].symbol2:
            local_watchlist.append(user.watchlist[0].symbol2)
        if user.watchlist[0].symbol3:
            local_watchlist.append(user.watchlist[0].symbol3)
        if user.watchlist[0].symbol4:
            local_watchlist.append(user.watchlist[0].symbol4)  
    watchlist_cards=[]   
    for symbol in local_watchlist:
        watchlist_cards.append(sd.get_stock_card(symbol))

    return render_template(
        "stockdata.html",
        stock_card_data=stock_card_data,
        stock_detail_data=stock_detail_data,
        plot_div=plot_div,

        nifty50_data=nifty50_data,
        sensex_data=sensex_data,
        news_articles=news_articles,
        watchlist=watchlist_cards,
    )



@app.route("/stonks")
def stonks():
    return render_template("stonks.html")


@app.route("/plot_compare", methods=["GET", "POST"])
def plot_compare():
    symbol_1 = symbol_2 = symbol_3 = error = plot_div = ""

    if request.method == "POST":
        symbol_1 = request.form.get("stock1").upper()
        symbol_2 = request.form.get("stock2").upper()
        symbol_3 = request.form.get("stock3").upper()
        parameter = request.form.get("stock_parameter")


        plot_div = sp.plot_and_compare_symbols(
            symbol_1, symbol_2, symbol_3, parameter, height=600, width=1000
        )
        if plot_div is None:
            plot_div = ""
            error = "Please enter valid stock symbols"

    return render_template(
        "plot_compare.html",
        plot_div=plot_div,
        stock1=symbol_1,
        stock2=symbol_2,
        stock3=symbol_3,
        error=error,
        parameter_options=sd.get_stock_compare_parameters(),
        news_articles=news_articles,
        nifty50_data=nifty50_data,
        sensex_data=sensex_data,
    )


@app.route("/reset_filter")
def reset_filter():
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    return redirect(url_for("index"))

@app.route("/nav-bar")
def nav_bar():
    return render_template("./static/nav-bar.html")

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
