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

### General Information

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