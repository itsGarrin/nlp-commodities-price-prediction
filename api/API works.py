#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 14:05:56 2024

@author: jianihe
"""

import pandas as pd
import requests
import yfinance as yf


def alpha_vantage(tick, api_key, frequency = 'DAILY'):
    """
    The function to use API to download stock historical price data

    Parameters
    ----------
    tick : string
        The ticker of the stock/rate you choose
    api_key : string
        Aplha Vantage API key

    Returns
    -------
    a list of series of adjusted close price

    """
    #Using API to get data
    key='&apikey=' + api_key
    ticker='&symbol=' + tick
    endpoint='function=TIME_SERIES_' + frequency + "_ADJUSTED"
    size='&outputsize=full'
    web='https://www.alphavantage.co/query?'
    url =web+endpoint+ticker+size+key
    
    r = requests.get(url)
    print(r.status_code) #Check the status of API, a response of 200 means success, 404 means url not found
    data = r.json()
    
    r1=data['Time Series (Daily)']

    keys_list=list(r1.keys())
    
    clean = pd.DataFrame(columns=['Date', tick + '_adj_close']) #creating an empty dataframe where prices will be stored
    clean.set_index('Date', inplace=True)
    
    for j in range(len(keys_list)):
        date=keys_list[j]
        adj_close = float(r1[date]['5. adjusted close'])
        clean.loc[date] = adj_close
    
    #make sure it's in chronological order
    clean = clean.sort_index(ascending=True)
    
    #Set time horizon
    start_date = '2011-08-11'
    end_date = '2021-08-12'
    clean = clean.loc[start_date:end_date]
    clean.index = pd.to_datetime(clean.index).strftime('%Y-%m-%d')
    
    #calculate returns
    clean[tick + ' return'] = clean[tick + '_adj_close'].pct_change()
    
    return clean

def yfinance(tick):
    data = yf.download(tick, start="2011-08-11", end="2021-08-12", interval="1d")[['Adj Close']]
    data.columns = [tick]
    data.index = data.index.strftime('%Y-%m-%d')
    return data

if __name__ == "__main__":
    key = "D32EVZCEU7HZUFYQ"
    
    #create a dataframe to store all data
    historical_data = pd.DataFrame(columns=['Date', 'crude_oil', 'CPI', 'Fed Fund Rate']) #creating an empty dataframe where prices will be stored
    historical_data.set_index('Date', inplace=True)
    
    #load Crude Oil
    url = 'https://www.alphavantage.co/query?function=BRENT&interval=daily&apikey=' + key 
    r = requests.get(url)
    data = r.json()
    
    r1=data["data"]
    
    for j in range(len(r1)):
        date=r1[j]["date"]
        price = r1[j]['value']
        try:
            price = float(price)
            historical_data.loc[date, "crude_oil"] = price
        except ValueError:
            pass
    
    #Download CPI
    url = 'https://www.alphavantage.co/query?function=CPI&interval=monthly&apikey=' + key
    r = requests.get(url)
    data = r.json()
    
    r2=data["data"]
    
    for j in range(len(r2)):
        date=r2[j]["date"]
        value = r2[j]['value']
        try:
            value = float(value)
            historical_data.loc[date, "CPI"] = value
        except ValueError:
            pass
    
    #Download Fed funds Rate
    riskfree=[]
    url = 'https://www.alphavantage.co/query?function=FEDERAL_FUNDS_RATE&interval=daily&apikey='+key
    r = requests.get(url)
    data = r.json()
    
    r3=data["data"]
    
    for j in range(len(r3)):
        date=r3[j]["date"]
        value = r3[j]['value']
        try:
            value = float(value)
            historical_data.loc[date, "Fed Fund Rate"] = value
        except ValueError:
            pass
    
    #make sure it's in chronological order
    historical_data = historical_data.sort_index(ascending=True)
    
    #Set time horizon
    start_date = '2011-08-01' #need to be the first day of Aug to obtain CPI
    end_date = '2021-08-12'
    historical_data = historical_data.loc[start_date:end_date]
    historical_data.index = pd.to_datetime(historical_data.index).strftime('%Y-%m-%d')
    
    #calculate returns
    historical_data["crude_oil_return"] = historical_data['crude_oil'].pct_change()
    
    #forward fill CPI to daily
    historical_data['CPI'].fillna(method='ffill', inplace=True)
    
    #load historical price of SPY/DIA/QQQ
    SPY = alpha_vantage('SPY', key) #S&P500
    DIA = alpha_vantage('DIA', key) #Dow Jones
    QQQ = alpha_vantage('QQQ', key) #NASDAQ
    
    #Download Bitcoin/VIX/FSPSX/US Dollar Index (yfinance)
    bitcoin = yfinance("BTC-USD")
    vix = yfinance("^VIX")
    usd_index = yfinance("DX-Y.NYB")
    usd_index.rename(columns={'DX-Y.NYB': 'usd_index'}, inplace=True)
    fspsx = yfinance("FSPSX")
    fspsx['FSPSX_return'] = fspsx['FSPSX'].pct_change()

    
    #Combined all data 
    historical_data = pd.concat([SPY, DIA, QQQ, historical_data, bitcoin, vix, fspsx, usd_index], axis=1)
    print(historical_data)
    
    #Reset time horizon
    start_date = '2011-08-12' #need to be the first day of Aug to obtain CPI
    end_date = '2021-08-12'
    historical_data = historical_data.loc[start_date:end_date]
    historical_data = historical_data.sort_index(ascending=True)
    
    historical_data.to_csv('/Users/jianihe/Desktop/historical data.csv')


