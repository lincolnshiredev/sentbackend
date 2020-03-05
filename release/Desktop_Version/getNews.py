from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
from newsapi import NewsApiClient
import pandas as pd
import dateparser
import requests
import string
import time
import json
# https://us-central1-enhanced-bebop-268815.cloudfunctions.net/getArticles?ticker=

sia = SentimentIntensityAnalyzer()

date = (datetime.now()).strftime("%Y-%m-%d")# - timedelta(days=1)

newsapi = NewsApiClient(api_key='d1303aa27f3840d9a0c5da1cccfc171b')
headers = {'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com",
           'x-rapidapi-key': "api key here"}

def getNewsApiArticles(ticker: str, date):
    
    print('Getting Artices from News API')
    newsApiDf = newsapi.get_everything(q=ticker,
                                          from_param=date,
                                          language='en',
                                          page=1)

    newsApiDf = pd.DataFrame(newsApiDf)
    newsApiDf = pd.concat([newsApiDf.drop(
        ['articles'], axis=1), newsApiDf['articles'].apply(pd.Series)], axis=1)
    
    newsApiDf.drop_duplicates(subset="title",
                                 keep=False, inplace=True)
    
    for index, row in newsApiDf.iterrows():
        time1 =  dateparser.parse(str(row['publishedAt'])) 
        time1 = int(time.mktime(time1.timetuple()))
        time1 = time.gmtime(time1)
        time1 = time.strftime("%Y-%m-%d", time1)
        newsApiDf.loc[index, 'publishedAt'] = time1
        #newsApiDf = newsApiDf[newsApiDf['publishedAt'] == date] # this overrides the time, do we want that?

    for index, row in newsApiDf.iterrows():
        newsApiDf.loc[index, 'sourceName'] = (
            (((str(row['source']).split("'name': '", 1))[1]).split("'}", 1))[0])
        
    print("Successfully got articles from News API")

    return newsApiDf


def getYahooNewsArticles(ticker: str):
    print('Getting Articles from Yahoo')
    querystring = {"category": ticker, "region": "US"}

    yahooNews = requests.get(url='https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-newsfeed',
                        headers=headers, params=querystring)

    yahooNewsDf = pd.read_json(json.dumps((yahooNews.json())['items']['result']))
    yahooNewsDf = yahooNewsDf.drop(columns=['uuid', 'main_image','entities', 'ignore_main_image', 'streams',
                          'offnet', 'reference_id', 'is_magazine', 'type', 'author'])
    yahooNewsDf['summary'] = yahooNewsDf['summary'].str.lower()
    yahooNewsDf['content'] = yahooNewsDf['content'].str.lower()

    for index, row in yahooNewsDf.iterrows():
        yahooNewsDf.loc[index, 'sentiment'] = sentiment(row['summary'])
        yahooNewsDf.loc[index, 'urlToImage'] = "https://images.pexels.com/photos/102720/pexels-photo-102720.jpeg" 
        # Example stock image, by: Markus Spiske, hosted on: https://www.pexels.com/
    
    yahooNewsDf = yahooNewsDf[yahooNewsDf['sentiment'] != 0]
    
    yahooNewsDf.rename(columns={'published_at': 'publishedAt',
                        'summary': 'description', 'link': 'url','publisher':'sourceName'}, inplace=True)
   
    yahooNewsDf = yahooNewsDf.drop(columns=['content','description'])
   
    print("successfully retrieved articles from yahoo and performed sentiment analysis")
    return yahooNewsDf


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


newsApiDf = pd.DataFrame()
yahooNewsDf = pd.DataFrame() 

numberOfArticles:int = 0
overallSentiment: float = 0.0

tickers = ["aapl"]

for ticker in tickers:
    newsApiDf = newsApiDf.append(getNewsApiArticles(ticker, date), sort=True)
    yahooNewsDf = yahooNewsDf.append(getYahooNewsArticles(ticker))


for ind,row in yahooNewsDf.iterrows():
    overallSentiment  = overallSentiment+row['sentiment']
    numberOfArticles = numberOfArticles + 1


if (len(newsApiDf) != 0):
   
    newsApiDf = runSent(newsApiDf)
   
    for ind, row in newsApiDf.iterrows():
        overallSentiment = overallSentiment+row['sentiment']
        numberOfArticles = numberOfArticles + 1
    
    newsApiDf = newsApiDf.drop(columns=['content','description','status','totalResults','author','source'])
    newsApiDf = newsApiDf.append(yahooNewsDf,sort=True)
    
    avgSentiment:float = overallSentiment/numberOfArticles
    valuesDict ={"numberOfArticles":numberOfArticles,"overallSentiment":overallSentiment,"avgSentiment": ("{0:.2f}".format(avgSentiment))}

    newsApiDict = newsApiDf.to_dict(orient='records')

    newsApiDf.drop

    newsArticlesDict = {'articles ':newsApiDict,'additionalData':valuesDict}

    jsonresp = json.dumps(newsArticlesDict, default=str)
else:
    print('no results for news api')
    
    yahooNewsDict = yahooNewsDf.to_dict(orient='records')
    newsArticlesDict = {'articles':yahooNewsDict,'additionalData':valuesDict}

    jsonresp = json.dumps(newsArticlesDict, default=str)

print(jsonresp)