#!/usr/bin/env python

# Requirements:
# pip install yfinance

# Parameter file in json format with the following keys:
# - watch_list: list of stock symbols to watch
# - ticker2name: stock symbol to name conversion table
# - portfolio: dictionary containing the keys:
#   - stock_file: file containing stock data
#   - dividend_file: file containing dividend data

import json
import pandas as pd
import pandas_datareader as pdr
import yfinance as yf


def load_params(parameter_file):
    with open(parameter_file, 'r') as f:
        data = f.read()
    return json.loads(data)


def invert_dictionary(d):
    new_dict = {}
    for k, v in d.items():
        new_dict[v] = k
    return new_dict


def main():
    data = load_params("stocks.json")
    watch_list = data['watch_list']
    ticker2name = data['ticker2name']
    name2ticker = invert_dictionary(ticker2name)
    stock_file = data["portfolio"]["stock_file"]
    dividend_file = data["portfolio"]["dividend_file"]

    print(json.dumps(watch_list, indent=2))
    print(json.dumps(ticker2name, indent=2))
    print(json.dumps(name2ticker, indent=2))


if __name__ == "__main__":
    main()
