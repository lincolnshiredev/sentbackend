from newsapi import NewsApiClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
import time
import pandas as pd
import string
import requests
import json
import dateparser

sia = SentimentIntensityAnalyzer()
date = (datetime.now()- timedelta(days=1)).strftime("%Y-%m-%d")
newsapi = NewsApiClient(api_key='d1303aa27f3840d9a0c5da1cccfc171b')
headers = {'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com",
           'x-rapidapi-key': "8d02ef92a9mshbe032b4fec7a9bfp15eb07jsn6fc9e511caff"}
tickers = ["aapl"]


def requestProfile(ticker: str):
    stock = requests.get(
        url='https://us-central1-enhanced-bebop-268815.cloudfunctions.net/stockData?ticker=' + ticker)
    print('Getting Current Price for ' + ticker)
    return json.dumps((stock.json())['companyData']['profile']['price'])


def getNewsApiArticles(ticker, date):
    print('Getting Artices from News API')
    newsApiDf = newsapi.get_everything(q=ticker,
                                          from_param=date,
                                          language='en',
                                          page=1)

    newsApiDf = pd.DataFrame(newsApiDf)
    newsApiDf = pd.concat([newsApiDf.drop(
        ['articles'], axis=1), newsApiDf['articles'].apply(pd.Series)], axis=1)
    newsApiDf["ticker"] = ticker
    newsApiDf["lastPrice"] = requestProfile(ticker)
    newsApiDf.drop_duplicates(subset="title",
                                 keep=False, inplace=True)
    print("Successfully got articles from News API")
    return newsApiDf


def getYahooNewsArticles(ticker):
    print('Getting Articles from Yahoo')
    querystring = {"category": ticker, "region": "US"}

    yahooNews = requests.get(url='https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-newsfeed',
                        headers=headers, params=querystring)

    yahooNewsdf = pd.read_json(json.dumps((yahooNews.json())['items']['result']))
    yahooNewsdf = yahooNewsdf.drop(columns=['uuid', 'main_image', 'entities', 'ignore_main_image', 'streams',
                          'offnet', 'reference_id', 'is_magazine', 'type', 'publisher', 'author'])
    yahooNewsdf['summary'] = yahooNewsdf['summary'].str.lower()
    yahooNewsdf['content'] = yahooNewsdf['content'].str.lower()
    yahooNewsdf["lastPrice"] = requestProfile(ticker)

    for index, row in yahooNewsdf.iterrows():
        yahooNewsdf.loc[index, 'ticker'] = ticker
        yahooNewsdf.loc[index, 'sentiment'] = sentiment(row['summary'])

    yahooNewsdf = yahooNewsdf[yahooNewsdf['sentiment'] != 0]
    print("successfully retrieved articles from yahoo and performed sentiment analysis")
    return yahooNewsdf


def sentiment(text):
    return sia.polarity_scores(text)['compound']


def runSent(dataFrame):
    print('Perfoming Sentiment Analysis on news api')
    for index, row in dataFrame.iterrows():
        if (row['description'] != None):
            sentVal = sentiment(row['description'])
            dataFrame.loc[index, 'sentiment'] = sentVal
            sentVal = 0
        else:
            sentVal = sentiment(row['content'])
            dataFrame.loc[index, 'sentiment'] = sentVal
            sentVal = 0

    dataFrame = dataFrame[dataFrame['sentiment'] != 0]
    print('Sentiment Analysis Complete on news api')
    return dataFrame


newsApiDf = pd.DataFrame() #df
yahooNewsDf = pd.DataFrame() #df2


for ticker in tickers:
    newsApiDf = newsApiDf.append(getNewsApiArticles(ticker, date), sort=True)
    yahooNewsDf = yahooNewsDf.append(getYahooNewsArticles(ticker))


if (len(newsApiDf) != 0):
    newsApiDf = runSent(newsApiDf)
    newsApiDf = newsApiDf[['publishedAt', 'title', 'description', 'url',
             'ticker', 'sentiment', 'lastPrice']]
    yahooNewsDf.rename(columns={'published_at': 'publishedAt',
                        'summary': 'description', 'link': 'url'}, inplace=True)
    yahooNewsDf = yahooNewsDf[['publishedAt', 'title', 'description', 'url',
               'ticker', 'sentiment', 'lastPrice']]
    
    # newsApiDict = newsApiDf.to_dict()
    # yahooNewsDict = yahooNewsDf.to_dict()
    
    # newsArticlesDict = {'newsApi':newsApiDict,'yahooNews':yahooNewsDict}
    
    newsApiDf.append(yahooNewsDf, sort=True)

    newsApiDf = newsApiDf[['publishedAt', 'title', 'description', 'url',
             'ticker', 'sentiment', 'lastPrice']]
else:
    print('no results for news api')
    yahooNewsDf.rename(columns={'published_at': 'publishedAt',
                        'summary': 'description', 'link': 'url'}, inplace=True)
    yahooNewsDf = yahooNewsDf[['publishedAt', 'title', 'description', 'url',
               'ticker', 'sentiment', 'lastPrice']]
    newsApiDf = yahooNewsDf
    newsApiDf = newsApiDf[['publishedAt', 'title', 'description', 'url',
             'ticker', 'sentiment', 'lastPrice']]


for index, row in newsApiDf.iterrows():
    time1 =  dateparser.parse(str(row['publishedAt'])) 
    time1 = int(time.mktime(time1.timetuple()))
    time1 = time.gmtime(time1)
    time1 = time.strftime("%Y-%m-%d", time1)
    newsApiDf.loc[index, 'publishedAt'] = time1


newsApiDf = newsApiDf[newsApiDf['publishedAt'] == date]


jsonresp = newsApiDf.to_json(orient='records')


print(jsonresp)
