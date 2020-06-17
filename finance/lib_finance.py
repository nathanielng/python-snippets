#!/usr/bin/env python

# Requirements:
# pip install pandas-datareader yfinance

# Parameter file in json format with the following keys:
# - watch_list: list of stock symbols to watch
# - ticker2name: stock symbol to name conversion table
# - portfolio: dictionary containing the keys:
#   - stock_file: file containing stock data
#   - dividend_file: file containing dividend data

import datetime
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


def retrieve_ticker(ticker, start, end, src='yahoo'):
    df = pdr.data.DataReader(ticker, src, start, end)
    return df


def retrieve_last_week(ticker, **kwargs):
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=7)
    df = retrieve_ticker(ticker, start, end, **kwargs)
    return df


def retrieve_last_time_periods(ticker, periods={'last month': 30, 'last quarter': 90, 'last 6 months': 182, 'last year': 365, 'last 2 years': 730, 'last 5 years': 1825},
                               **kwargs):
    """
    Retrieves data from 1 month, 3 months, 6 months,
    1 year, 2 years, and 5 years ago.
    Uses a 5 day window (in case of holidays)
    """
    now = datetime.datetime.now()
    df = pd.DataFrame()
    for label, days in periods.items():
        dt1 = now - datetime.timedelta(days=days+2)
        dt2 = now - datetime.timedelta(days=days-2)
        df_temp = retrieve_ticker(ticker, dt1, dt2, **kwargs)
        df_temp = df_temp.sort_values('Volume', ascending=False).iloc[0]
        df_temp['Period'] = label
        df = df.append(
            df_temp
        )
    return df


class Portfolio():

    def __init__(self, parameter_file):
        data = load_params(parameter_file)
        self.watch_list = data['watch_list']
        self.ticker2name = data['ticker2name']
        self.name2ticker = invert_dictionary(self.ticker2name)
        self.stock_file = data['portfolio']['stock_file']
        self.dividend_file = data['portfolio']['dividend_file']

    def load_csv_data(self):
        self.stocks = pd.read_csv(self.stock_file, header=1)
        self.dividends = pd.read_csv(self.dividend_file, header=0).dropna(how='all')

    def info(self):
        earliest_date = self.stocks['Contract Date'].min()
        print(f'Earliest date: {earliest_date}')
        print(json.dumps(self.ticker2name, indent=2))
        print(json.dumps(self.name2ticker, indent=2))
        print(self.stocks)
        print(self.dividends)

    def print_watch_list(self):
        for ticker in self.watch_list:
            stock_name = self.ticker2name[ticker]
            print(f'----- {stock_name} ({ticker}) -----')
            df = retrieve_last_week(ticker)
            print(df)
            df = retrieve_last_time_periods(ticker)
            print(df)


def main():
    P = Portfolio("stocks.json")
    P.load_csv_data()
    P.info()
    P.print_watch_list()


if __name__ == "__main__":
    main()
