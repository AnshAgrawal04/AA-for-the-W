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
import get_stock_data as gsd
from bokeh.models import Button, CustomJS
from bokeh.layouts import layout

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

# Initialize Database within Application Context
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.')
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        session['username'] = user.username
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid username or password')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return redirect(url_for('graph'))
        return render_template('welcome.html', username=session['username'])
    else:
        return redirect(url_for('index'))

@app.route('/graph')
def graph():
    period = request.args.get('period', default="1Y", type=str)
    if period == "1Y":
        days = 365
    elif period == "6M":
        days = 182
    elif period == "1M":
        days = 30
    elif period == "5D":
        days = 5
    elif period == "5Y":
        days = 5*365
    else:
        days = 365  # default to 1 year if period is not recognized
    p = gsd.get_index_data("NIFTY 50", days)
    script, div = components(p)
    return render_template('graph.html', script=script, div=div, cdn_js=CDN.js_files[0])

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
