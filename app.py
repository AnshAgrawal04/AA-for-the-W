from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import get_stock_data as gsd
from plotly.offline import plot

nifty_50 = list(pd.read_csv("ind_nifty50list.csv")["Symbol"])

def get_paramter_from_string(parameter):
    if parameter == 'Closing Price':
        return 'CLOSE'
    elif parameter == 'Opening Price':
        return 'OPEN'
    elif parameter == 'High Price':
        return 'HIGH'
    elif parameter == 'Low Price':
        return 'LOW'
    elif parameter == 'Volume':
        return 'VOLUME'
    else:
        return 'CLOSE'

def plot_and_compare_symbols(symbol_name_1, symbol_name_2, symbol_name_3,parameter):
    num_years = 2
    days = 365 * num_years
    para=get_paramter_from_string(parameter)
    fig = gsd.get_plot(
        gsd.get_symbol_data(symbol_name_1, days), symbol_name_1, "DATE", para, parameter)
    fig = gsd.add_trace(
        fig,
        gsd.get_symbol_data(symbol_name_2, days),
        symbol_name_2,
        "DATE",
        para, parameter
    )
    if symbol_name_3 in nifty_50:
        fig = gsd.add_trace(
            fig,
            gsd.get_symbol_data(symbol_name_3, days),
            symbol_name_3,
            "DATE",
            para, parameter
        )
    plot_div = plot(
        fig,
        output_type="div",
        include_plotlyjs=False,
        config={"displayModeBar": False},
    )
    return render_template(
        "plot_compare_graph.html",
        plot_div=plot_div,
        stock1=symbol_name_1,
        stock2=symbol_name_2,
        stock3=symbol_name_3,
    )

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
    if "user_id" in session:
        return redirect(url_for("graph"))
        return render_template("welcome.html", username=session["username"])
    else:
        return redirect(url_for("index"))


@app.route("/index_graph")
def index_graph():
    num_years = 2
    days = 365 * num_years
    fig = gsd.get_plot(
        gsd.get_index_data("NIFTY 50", days), "NIFTY 50", "HistoricalDate", "CLOSE"
    )
    plot_div = plot(
        fig, output_type="div", include_plotlyjs=False, config={"displayModeBar": False}
    )
    return render_template("graph.html", plot_div=plot_div)


@app.route("/plot_compare", methods=["GET", "POST"])
def plot_compare():
    parameter_options = ['Closing Price', 'Opening Price', 'High Price', 'Low Price', 'Volume']
    if request.method == "POST":
        symbol_name_1 = request.form.get("stock1")
        symbol_name_2 = request.form.get("stock2")
        symbol_name_3 = request.form.get("stock3")
        parameter = request.form.get("stock_parameter")
        if symbol_name_1 not in nifty_50 or symbol_name_2 not in nifty_50:
            return render_template(
                "plot_compare.html",parameter_options=parameter_options, error="Please enter valid stock symbols"
            )
        return plot_and_compare_symbols(symbol_name_1, symbol_name_2, symbol_name_3, parameter)

    return render_template("plot_compare.html",parameter_options=parameter_options)


@app.route("/reset", methods=["POST"])
def plot_compare_graph():
    if request.method == "POST":
        return redirect(url_for("plot_compare"))


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)

