from datetime import datetime
import pandas as pd
import requests
import json
import ast

def requestProfile(ticker: str): 
    # Gets company information as well as the current share price
    stock= requests.get(url='https://financialmodelingprep.com/api/v3/company/profile/' + ticker)
    return(pd.read_json(json.dumps(stock.json()))) 
    # Converts the json data result into a Pandas Dataframe which is returned

def requestData(ticker: str, days: int): 
    # Gets historic open and close prices for the stock based on how many days in the past you wish to view
    stock= requests.get(url='https://financialmodelingprep.com/api/v3/historical-price-full/' + ticker + '?timeseries=' + str(days))
    return (pd.read_json(json.dumps(stock.json())))

def request(ticker: str,days: int): 
    # Calls the functions and then removes data that is not required 
    companyInfoDf: pd.Dataframe = requestProfile(ticker)
    historicDataDf: pd.DataFrame = requestData(ticker,days)
    
    historicDataDf = historicDataDf.drop(columns=['symbol'])
    companyInfoDf = companyInfoDf.drop(columns=['symbol'])
    companyInfoDf = companyInfoDf.drop(['beta','changes','changesPercentage','description','image','industry','lastDiv','mktCap','range','volAvg'])
    
    # Converts the dataframes to a dictionary and then to json which is returned
    profileDict = companyInfoDf.to_dict()
    
    date = (datetime.now()).strftime("%Y-%m-%d")
    
    price = requests.get(url='https://financialmodelingprep.com/api/v3/stock/real-time-price/' + ticker)
    stockPriceDf = pd.DataFrame([pd.read_json(json.dumps(price.json()),typ = 'series')])
    # Requests the live price for the ticker and then stores it in a dataframe

    livePriceDf = pd.DataFrame({"historical":[{'date': date, 'open': 0, 'high': 0, 'low': 0, 'close':  (str(stockPriceDf.loc[0,'price'])) , 'adjClose': 0, 'volume': 0, 'unadjustedVolume': 0, 'change': 0, 'changePercent': 0, 'vwap': 0, 'label': 'N/a', 'changeOverTime': 0}]})
    # A Pandas DataFrame is created in the same format as the historic data DataFrame but containing 
    # todays date and the current live price
    
    historicDataDf = livePriceDf.append(historicDataDf)
    # The two dataFrames are appended 
    historicDict = historicDataDf.to_dict(orient='records')
    
    combinedDict = {'companyData':profileDict,'data':historicDict}
    
    return json.dumps(combinedDict)
    
tickers: str = ['aapl']
# Example tickers for companies, case insensitive

for ticker in tickers:
    print(request(ticker,7)) 
    # Ticker then the number of days you wish to get historic data for
    