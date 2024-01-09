import os
from cs50 import SQL

from flask import Flask, flash, redirect, render_template, request, jsonify, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
import pandas_ta as ta
from helpers import apology, login_required, lookup, usd
from lightweight_charts import Chart
import requests
import logging


app = Flask(__name__)


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")
logging.getLogger('yfinance').setLevel(logging.ERROR)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    user_id = session["user_id"]
    transactions_db = db.execute("SELECT symbol, SUM(shares) AS shares, price FROM transactions WHERE user_id = ? GROUP BY symbol", user_id)
    cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
    cash = cash_db[0]["cash"]

    total_stock_value = sum([row["shares"] * row["price"] for row in transactions_db])

    remaining_cash = cash + total_stock_value

    general_news = get_general_stock_news()

    if not user_id:
        return render_template("register.html")

    """Show portfolio of stocks"""
    return render_template("index.html", database = transactions_db, cash = cash, remaining_cash=remaining_cash, general_news=general_news)



@app.route('/graph', methods=['GET', 'POST'])
def graph():
    if request.method == 'POST':
        symbol = request.form['symbol']
        interval = request.form['interval']
        indicator = request.form['indicator']  # Get the selected indicator

        data, smaData, rsiData = get_stock_data(symbol, interval, indicator)  # Update function accordingly

        return jsonify({
            'data': data,
            'smaData': smaData,
            'rsiData': rsiData  # Include Bollinger Bands data in the response
        })
    return render_template('graph.html')

def get_stock_data(symbol, interval, indicator):
    stock = yf.Ticker(symbol)
    df = stock.history(period="5y", interval=interval)  # Use the selected interval

    data = None
    smaData = None
    rsiData = None

    if indicator == 'SMA':
        sma = df.ta.sma(length=20)
        sma = sma.reset_index()
        sma = sma.rename(columns={"Date": "time", "SMA_20": "value"})
        sma = sma.dropna()
        df.reset_index(inplace=True)
        df.columns = df.columns.str.lower()
        data = df.to_dict(orient='records')
        smaData = sma.to_dict(orient='records')

    elif indicator == "RSI":
        rsi = df.ta.rsi()
        rsi = rsi.reset_index()
        rsi = rsi.rename(columns={"Date": "time", "RSI_14": "value"})
        rsi = rsi.dropna()
        df.reset_index(inplace=True)
        df.columns = df.columns.str.lower()
        data = df.to_dict(orient='records')
        rsiData = rsi.to_dict(orient='records')

    return data, smaData, rsiData



@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "GET":
        return render_template("buy.html")

    else:
        symbol = request.form.get("symbol").upper()
        shares = request.form.get("shares")
        if not symbol:
            return apology("Must provide symbol", 400)
        elif not shares or not shares.isdigit() or int(shares) <= 0:
            return apology("Must provide share amount", 400)

        quote = lookup(symbol)
        if quote == None:
            return apology("Insert valid symbol", 400)

        price = quote["price"]
        total_cost = int(shares) * price
        cash = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])[0]["cash"]

        if cash < total_cost:
            return apology("Not enough funds")

        db.execute("UPDATE users SET cash = cash - :total_cost WHERE id = :user_id",
                   total_cost=total_cost, user_id=session["user_id"])

        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (:user_id, :symbol, :shares, :price)",
                   user_id=session["user_id"], symbol=symbol, shares=shares, price=price)

        total_cost_usd = usd(total_cost)
        flash(f"Bought {shares} of {symbol} for usd {total_cost_usd}")
        return redirect("/")


@app.route("/history")
@login_required
def history():
    transactions = db.execute("SELECT * FROM transactions WHERE :user_id ORDER BY date DESC", user_id=session["user_id"])
    return render_template("history.html", transactions=transactions)


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "GET":
        return render_template("quote.html")

    else:
        symbol = request.form.get("symbol")
        quote = lookup(symbol)
        if not quote:
            return apology("must provide symbol", 400)
        return render_template("quote.html", quote=quote)




@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":

        if not request.form.get("username"):
            return apology("must provide username", 400)

        if not request.form.get("password"):
            return apology("must provide password", 400)

        if not request.form.get("confirmation"):
            return apology("must provide password confirmation", 400)

        if request.form.get("password") != request.form.get("confirmation"):
            return apology("must provide identical password and confirmation", 400)

        hash = generate_password_hash(request.form.get("password"))

        try:
            new_user = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"), hash)
        except:
            return apology("Username already exists")
        session["user_id"] = new_user
        return redirect("/")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    symbols_user = db.execute("SELECT symbol, SUM(shares) as total_shares FROM transactions WHERE user_id = :user_id GROUP BY symbol HAVING total_shares > 0",
    user_id=session["user_id"])

    if request.method == "GET":
        user_id = session["user_id"]
        return render_template("sell.html", symbols = [row["symbol"] for row in symbols_user])

    else:
        symbol = request.form.get("symbol").upper()
        shares = request.form.get("shares")
        if not symbol:
            return apology("Must provide symbol", 400)
        elif not shares or not shares.isdigit() or int(shares) <= 0:
            return apology("Must provide share amount", 400)
        else:
            shares = int(shares)

        for stock in symbols_user:
            if stock["symbol"] == symbol:
                if stock["total_shares"] < shares:
                    return apology("not enough shares", 400)
                else:
                    quote = lookup(symbol)
                    if quote is None:
                        return apology("symbol not found", 400)
                    price = quote["price"]
                    total_sale = shares * price

                    db.execute("UPDATE users SET cash = cash + :total_sale  WHERE id= :user_id",
                               total_sale = total_sale, user_id=session["user_id"])

                    db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (:user_id, :symbol, :shares, :price)",
                    user_id=session["user_id"], symbol=symbol, shares=-shares, price=price)

                    price_usd = usd(total_sale)
                    flash(f"Sold! {shares} for {price_usd}")
                    return redirect("/")
        return apology("symbol not found", 400)

@app.route("/addcash", methods = ["GET", "POST"])
@login_required
def addcash():
    if request.method == "GET":
        return render_template("addcash.html")
    else:
        new_cash = int(request.form.get("new_cash"))

        if not new_cash:
            return apology("Give cash", 400)
        user_id = session["user_id"]
        user_cash_db = db.execute("SELECT cash FROM users WHERE id = :id", id=user_id)
        user_cash = user_cash_db[0]["cash"]

        uptd_cash = user_cash + new_cash
        db.execute("UPDATE users SET cash = ? WHERE id = ?", uptd_cash, user_id)

        return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route('/stock_info/<symbol>')
def stock_info(symbol):
    API_KEY = 'RYKWN6PR4TFS8YAL'  # Replace with your API key
    ENDPOINT = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={API_KEY}"

    response = requests.get(ENDPOINT)
    data = response.json()

    news_articles = get_stock_news(symbol)
    data['news_articles'] = news_articles

    market_cap_str = data.get('MarketCapitalization')
    market_cap_in_billions = None
    if market_cap_str:
        try:
            market_cap_float = float(market_cap_str)
            market_cap_in_billions = market_cap_float / 1e9
        except ValueError:
            pass
    formatted_market_cap = "{:.2f}B".format(market_cap_in_billions) if market_cap_in_billions else None

    # Convert and format EBITDA
    ebitda_str = data.get('EBITDA')
    ebitda_in_millions = None
    if ebitda_str:
        try:
            ebitda_float = float(ebitda_str)
            ebitda_in_millions = ebitda_float / 1e9
        except ValueError:
            pass
    formatted_ebitda = "{:.2f}B".format(ebitda_in_millions) if ebitda_in_millions else None

    dividend_yield_float = float(data.get('DividendYield', 0))  # Converts the string to float
    formatted_dividend_yield = "{:.2%}".format(dividend_yield_float)  # Formats it as a percentage


    info = {
        'symbol': data.get('Symbol'),
        'asset_type': data.get('AssetType'),
        'name': data.get('Name'),
        'description': data.get('Description'),
        'exchange': data.get('Exchange'),
        'sector': data.get('Sector'),
        'industry': data.get('Industry'),
        'address': data.get('Address'),
        'fiscal_year_end': data.get('FiscalYearEnd'),
        'market_cap': formatted_market_cap,
        'ebitda': formatted_ebitda,
        'pe_ratio': data.get('PERatio'),
        'dividend_per_share': data.get('DividendPerShare'),
        'dividend_yield': formatted_dividend_yield,
        'news_articles': news_articles
    }



    return render_template('stock_info.html', **info)


def get_stock_news(ticker):
    API_KEY = 'b98b867146a0435896acc200476e6cbc'
    URL = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={API_KEY}"
    response = requests.get(URL)
    if response.status_code == 200:
        articles = response.json().get('articles', [])
        return articles[:3]
    return []

def get_stock_news_new(ticker):
    API_KEY = 'b98b867146a0435896acc200476e6cbc'
    URL = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={API_KEY}"
    response = requests.get(URL)
    if response.status_code == 200:
        articles = response.json().get('articles', [])
        return articles[:5]
    return []

def get_general_stock_news():
    API_KEY = 'b98b867146a0435896acc200476e6cbc'
    URL = f"https://newsapi.org/v2/top-headlines?q=market&apiKey={API_KEY}&language=en&sortBy=publishedAt&category=business"
    response = requests.get(URL)
    if response.status_code == 200:
        articles = response.json().get('articles', [])
        return articles[:10]
    return []

@app.route("/news", methods=["GET", "POST"])
@login_required
def news():
    if request.method == "POST":
        topic = request.form.get("topic")
        articles = get_stock_news_new(topic)
        return render_template("news.html", general_news=articles)

    general_news = get_general_stock_news()
    return render_template("news.html", general_news=general_news)

@app.route('/indices-data', methods=['GET'])
def get_indices_data():
    indices = ["^AEX", "^STOXX50E", "^IXIC", "^GSPC", "^GDAXI"]

    # Dictionary to map ticker symbols to their display names
    index_names = {
        "^AEX": "AEX",
        "^STOXX50E": "EUROSTOXX 50",
        "^IXIC": "NASDAQ",
        "^GSPC": "S&P 500",
        "^GDAXI": "DAX"
    }

    data = []

    for index in indices:
        ticker = yf.Ticker(index)
        today_data = ticker.history(period="1d")

        if not today_data.empty:
            open_price = today_data.iloc[0]['Open']
            close_price = today_data.iloc[0]['Close']
            percentage_growth = ((close_price - open_price) / open_price) * 100

            data.append({
                "name": index_names.get(index, index),  # Get the display name or use the index itself if not found
                "price": close_price,
                "percentage_growth": percentage_growth
            })

    return jsonify(data)

@app.route('/index-details/<index_name>')
def index_details(index_name):
    API_KEY = 'RYKWN6PR4TFS8YAL'
    # Hardcoded list for the top 15 stocks in ^AEX index (add others as needed).
    indices_data = {
        "AEX": ["UNA.AS", "ADYEN.AS", "RAND.AS", "MT.AS", "KPN.AS", "ASRNL.AS", "REN.AS", "AGN.AS", "WKL.AS", "AD.AS"],
        "EUROSTOXX 50": ["UNA.AS", "ADYEN.AS", "RAND.AS", "MT.AS", "KPN.AS", "ASRNL.AS", "REN.AS", "AGN.AS", "WKL.AS", "AD.AS"],
        "NASDAQ": ["UNA.AS", "ADYEN.AS", "RAND.AS", "MT.AS", "KPN.AS", "ASRNL.AS", "REN.AS", "AGN.AS", "WKL.AS", "AD.AS"],
        "S&P 500": ["UNA.AS", "ADYEN.AS", "RAND.AS", "MT.AS", "KPN.AS", "ASRNL.AS", "REN.AS", "AGN.AS", "WKL.AS", "AD.AS"],
        "DAX": ["UNA.AS", "ADYEN.AS", "RAND.AS", "MT.AS", "KPN.AS", "ASRNL.AS", "REN.AS", "AGN.AS", "WKL.AS", "AD.AS"]
    }

    company_names = {
        "UNA.AS": "Unilever",
        "ADYEN.AS": "Adyen",
        "RAND.AS": "Randstad",
        "MT.AS": "ArcelorMittal",
        "KPN.AS": "Royal KPN",
        "ASRNL.AS": "ASR Nederland",
        "REN.AS": "RELX",
        "AGN.AS": "Aegon",
        "WKL.AS": "Wolters Kluwer",
        "AD.AS": "Koninklijke Ahold Delhaize",
    }

    stocks = []

    if index_name in indices_data:
        for symbol in indices_data[index_name]:
            # Fetching data from Alpha Vantage API
            global_quote_params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': API_KEY
            }
            response = requests.get('https://www.alphavantage.co/query', params=global_quote_params)
            if response.status_code == 200:
                quote_data = response.json()['Global Quote']
                # Extract and calculate the percentage change
                price = float(quote_data['05. price'])
                previous_close = float(quote_data['08. previous close'])
                percentage_growth = ((price - previous_close) / previous_close) * 100

                stocks.append({
                    'name': company_names.get(symbol, symbol),  # Alpha Vantage does not return the company name in GLOBAL_QUOTE, so we use the symbol
                    'price': price,
                    'percentage_growth': percentage_growth
                })
            else:
                print(f"Error fetching data for symbol: {symbol}")

    return render_template("index-details.html", stocks=stocks, index_name=index_name)





if __name__ == '__main__':
    app.run(debug=True)
