from flask import Flask, render_template, request, redirect, url_for, flash,jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from jugaad_data.nse import stock_df
from datetime import date, timedelta

import get_stock_data as gsd
import news as n

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
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

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


@app.route("/dashboard")
def dashboard():

    if 'user_id' in session:        
        stock_symbols = ['DRREDDY','EICHERMOT','GRASIM','HCLTECH','ADANIENT','ADANIPORTS','APOLLOHOSP','ASIANPAINT','AXISBANK','SBIN','LT']  # Add all your 50 stock symbols here
        stockdata={}

        # stock_symbols=gsd.get_nifty50()
        ascending_data = []
        for symbol in stock_symbols:
            stockdata[symbol]=gsd.get_live_symbol_data(symbol)
            ascending_data.append({'symbol':symbol,'pchange':stockdata[symbol]['pChange'],'price':stockdata[symbol]['lastPrice']})
        ascending_data = sorted(ascending_data, key=lambda x: x['pchange'])
        descending_data = ascending_data[::-1]

        plot_div=gsd.plot_index('NIFTY 50',width=600,height=400)
        
        return render_template('dashboard.html', username=session['username'],stocks_data=stockdata, dsc=descending_data[:5], asc=ascending_data[:5],plot_div=plot_div,news_articles=n.get_news()['articles'][:3])

    else:
        return redirect(url_for('index'))

@app.route('/<symbol>')
def stock(symbol):
    livedata=gsd.get_live_symbol_data(symbol)
    stockdata=gsd.get_symbol_data(symbol,1).iloc[0]
    stock_parameter=gsd.get_stock_display_parameters()
    plot_div = gsd.plot_symbol(symbol, 'Closing Price',450,900)
    return render_template('stockdata.html', symbol=symbol, stockpara=stock_parameter, livedata=livedata, historicaldata=stockdata, plot_div=plot_div)
    if "user_id" in session:
        return redirect(url_for("graph"))
        return render_template("welcome.html", username=session["username"])
    else:
        return redirect(url_for("index"))

@app.route("/index_graph")
def index_graph():
    plot_div=gsd.plot_index(width=500,height=400)
    return render_template("graph.html", plot_div=plot_div)


@app.route("/plot_compare", methods=["GET", "POST"])
def plot_compare():
    parameter_options = gsd.get_stock_compare_parameters()
    if request.method == "POST":
        symbol_name_1 = request.form.get("stock1")
        symbol_name_2 = request.form.get("stock2")
        symbol_name_3 = request.form.get("stock3")
        parameter = request.form.get("stock_parameter")
        plot_div = gsd.plot_and_compare_symbols(
            symbol_name_1, symbol_name_2, symbol_name_3, parameter,600,1000
        )
        if plot_div is None:
            return render_template(
                "plot_compare.html",
                parameter_options=parameter_options,
                error="Please enter valid stock symbols",
            )

        return render_template(
            "plot_compare.html",
            plot_div=plot_div,
            stock1=symbol_name_1,
            stock2=symbol_name_2,
            stock3=symbol_name_3,
            parameter_options=parameter_options,
        )
    return render_template("plot_compare.html", parameter_options=parameter_options)


@app.route("/reset", methods=["POST"])
def plot_compare_graph():
    if request.method == "POST":
        return redirect(url_for("plot_compare"))



@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    return redirect(url_for("index"))

@app.route("/news")
def news():
    return render_template("news_feed.html", news_articles=n.get_news()['articles'][:3])

if __name__ == "__main__":
    app.run(debug=True)
    
