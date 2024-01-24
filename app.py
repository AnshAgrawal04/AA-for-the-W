from flask import Flask, render_template, request, redirect, url_for, flash,jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from jugaad_data.nse import stock_df
from datetime import date, timedelta


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key


def get_stock_data(symbol):
    # This is a mockup. Replace this with your actual function to get stock data.
    end_date = date.today()
    start_date = end_date - timedelta(days=1) # get data for the last 30 days
    df = stock_df(symbol=symbol, from_date=start_date, to_date=end_date)
    req=['DATE','OPEN','HIGH','LOW','CLOSE','VOLUME','SYMBOL']
    df=df[req]
    return df.to_dict(orient='records')[0]

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
        stock_symbols = ['DRREDDY','EICHERMOT','GRASIM','HCLTECH','ADANIENT','ADANIPORTS','APOLLOHOSP','ASIANPAINT','AXISBANK']  # Add all your 50 stock symbols here
        stockdata={}
        ascending_data = []
        for symbols in stock_symbols:
            stockdata[symbols]=get_stock_data(symbols)
            ascending_data.append([stockdata[symbols]['CLOSE']-stockdata[symbols]['OPEN'],symbols])
        print(stockdata)
        ascending_data.sort()
        descending_data = ascending_data[::-1]
        return render_template('table.html', username=session['username'],stocks_data=stockdata,asc=ascending_data ,desc=descending_data)
    else:
        return redirect(url_for('index'))
    
@app.route('/stock_data/<symbol>')
def stock_data(symbol):
    return jsonify(get_stock_data(symbol))

@app.route('/<symbol>')
def stock(symbol):
    stockdata=get_stock_data(symbol)
    return render_template('stockdata.html', symbol=symbol,data=stockdata)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
    
