from sys import set_asyncgen_hooks
from flask import Flask, render_template, request
from patterns import patterns
import yfinance as yf
import os, csv
import pandas as pd
import talib

app = Flask(__name__)

@app.route("/")
def index():
    pattern = request.args.get('pattern', None)
    stocks = {}
    with open('./Data/sp500.csv') as f:
        for row in csv.reader(f):
            stocks[row[0]] = {
                'company': row[1]
            }
    
    print(stocks)
    if pattern:
        datafiles = os.listdir("./Data/Daily")
        for filename in datafiles:
            df = pd.read_csv(f"./Data/Daily/{filename}")
            fn = getattr(talib, pattern)
            symbol = filename.split('.')[0]
            try:
                result = fn(df['Open'], df['High'], df['Low'], df['Adj Close'])
                last = result.tail(1).values[0]           
                if last > 0:
                    stocks[symbol][pattern] = 'bullish'
                elif last < 0:
                    stocks[symbol][pattern] = 'bearish'
                else:
                    stocks[symbol][pattern] = None
            except:
                pass
    return render_template("index.html", patterns=patterns, stocks=stocks, curr_pattern=pattern)

@app.route('/snapshot')
def snapshot():
    with open("./Data/sp500.csv") as f:
        companies = f.read().splitlines()
        for company in companies:
            symbol = company.split(',')[0]
            df = yf.download(tickers=symbol, start='2021-01-01')
            df.to_csv(f'./Data/Daily/{symbol}.csv')