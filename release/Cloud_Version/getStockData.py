import pandas as pd
import requests
import json

# https://us-central1-enhanced-bebop-268815.cloudfunctions.net/stockData?ticker= &days=
# This code can be deployed to Google Cloud Functions 
def stockData(request):    
    # When the a REST request is made to the above API endpoint then this function is ran 
    request_json = request.get_json(silent=True)
    request_args = request.args
    
    ticker: str = ''
    days:str = '' 
       
    if request_json and 'ticker' in request_json:
        ticker = str(request_json['ticker'])
    elif request_args and 'ticker' in request_args:
        ticker = str(request_args['ticker'])
    else:
        ticker: str = 'AAPL'
    # If the request contains a specific ticker then that data is extracted for use
    # Otherwise we default the script to use AAPL to obtain company and stock data
        
    if request_json and 'days' in request_json:
        days = str(request_json['days'])
    elif request_args and 'days' in request_args:
        days = str(request_args['days'])
    else:
        days = '7'
    # If the request contains a specific number of days to collect historic data on then 
    # that timeframe is used, otherwise we set it to have a default value of 7
        
    stockProfile = requests.get(url='https://financialmodelingprep.com/api/v3/company/profile/' + ticker)
    # Gets company information as well as the current share price

    companyInfoDf = pd.read_json(json.dumps(stockProfile.json()))
    # Converts the JSON data into a Pandas Dataframe
    
    stockData = requests.get(url='https://financialmodelingprep.com/api/v3/historical-price-full/' + ticker + '?timeseries=' + days)
    # Gets historic open and close prices for the stock based on how many days in the past you wish to view
    
    historicDataDf = pd.read_json(json.dumps(stockData.json()))
    # Converts the JSON data into a Pandas Dataframe
      
    companyInfoDf = companyInfoDf.drop(columns=['symbol'])
    companyInfoDf = companyInfoDf.drop(['beta','changes','changesPercentage','description','mktCap','industry','lastDiv', 'range','volAvg'])
    # Removes data from the Dataframe that is not required

    historicDataDf = historicDataDf.drop(columns=['symbol'])
    # Removes data from the Dataframe that is not required

    profileDict = companyInfoDf.to_dict()
    historicDict = historicDataDf.to_dict(orient='records')
    
    combinedDict = {'companyData':profileDict,'data':historicDict}
    # Converts the dataframes to a dictionary and then to json which is returned

    return json.dumps(combinedDict)
