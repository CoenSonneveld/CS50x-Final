# Stock Analysis

## Video Demo
[Watch the demo on YouTube](https://www.youtube.com/watch?v=PkjV1nUhOwA)

## Description
Welcome to my CS50x final project assignment: Stock Analysis. This project is a simple yet powerful application for analyzing individual stocks. It extends the 'Finance' project completed in the previous week of CS50x.

### Key Features:
- Real-time stock data retrieval from Alpha Vantage and IEX API.
- Interactive user interface for portfolio management, stock trading, and financial news updates.
- Graph Generator for stocks allowing you to customize a timeframe and Techincal Indicator


## Getting Started

### Prerequisites
Libraries: See requirements.txt
 

```bash
# Example of installation commands
git clone https://github.com/SunnyB1234/CS50x-Final
cd CS50X FINAL
pip install -r requirements.txt
```

## File information

#### app.py
All the Flask routes are defined in here plus some necessary functions

#### finance.db
This is the database where the user data is stored. Such as username, stocks in portfolio and amount of stocks owned.

#### helpers.py

File with some helper functions that support the application

#### static
This folder cointains all necessary JavaScript and CSS files. graph.js is responsible for generating the graph and styles.css for the layouting of the page.

#### templates
This folder cointains all the necessary html files for the website.

## General information

#### Home page:
When you land on the homepage you need to make a username by registering a name and a password, these are stored in a database using SQL. After logging in you reach your personal portfolio page, each stock that you own can be investigated further by clicking on the name. This leads to a page showing detailed information about the stock such as Dividend Yield, 52-week high, Market Cap, and sector. This information is retrieved live from Alpha Vantage. Three news articles are also fetched live using the NewsAPI page. If individual stock data doesn't load next to news articles that means the Alpha Vantage API has reached its free limit.

#### Quote page:
On the quote page it is possible to retrieve a live price quote for any stock. It also shows the live updated price and growth for the day of 5 important indices. When these indices are clicked you are forwarded to a page that displays the performance of 10 stocks in that particular index. this is also done using yfinance and data from Yahoo finance. If Indices data doesn't load, that means the Alpha Vantage free API Has reached its rate limit.

#### Buy and Sell page:
These are basic pages where you can buy and sell stocks to add or remove from your portfolio. This is all stored in a SQL database.

#### Deposit page:
This page allows you to deposit extra money into your portfolio, this allows you to spend more and expand your portfolio.

#### Graph Page:
On the graph page you have the ability to perform actual analysis on the stock. By typing in a ticker, selecting an interval and a technical indicator you can take a closer look at the performance of a stock. For example you can get daily or weekly candles and choose between a Moving Average, RSI or Volume these are made using the pandas_ta python library. This chart is generated using JavaScript and the Tradingview Chart API.

#### News Page:
The news page shows 10 recent articles related to financial markets. But you can get more specific by using the search bar. This allows you to search a specific topic and it will deliver 5 recent articles on the matter. Allowing you to do more research on a specific topic. This page uses data from NewsAPI and the  article are generated through this API as well.
