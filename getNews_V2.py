from newsapi import NewsApiClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
import pandas as pd
import string
import requests
import json

sia = SentimentIntensityAnalyzer()

date = datetime.now().strftime("%Y-%m-%d")

newsapi = NewsApiClient(api_key='d1303aa27f3840d9a0c5da1cccfc171b')

tickers = [["msft", "microsoft"], ["aapl", "apple"],
           ["GME", "gamestop"], ["amzn", "amazon"]]


def requestProfile(ticker: str): 
  
    stock= requests.get(url='https://financialmodelingprep.com/api/v3/company/profile/' + ticker)
    return json.dumps((stock.json())['profile']['price'])

def get_articles(ticker,date):
    all_articles = newsapi.get_everything(q=ticker[0],
                                      from_param= date,
                                      language='en',
                                      page=1)

    all_articles = pd.DataFrame(all_articles)
    all_articles = pd.concat([all_articles.drop(['articles'], axis=1), all_articles['articles'].apply(pd.Series)], axis=1)
    all_articles["ticker"] = ticker[0]
    all_articles["company"] = ticker[1]
    all_articles["lastPrice"] = requestProfile(ticker[0])
    all_articles.drop_duplicates(subset ="title", 
                     keep = False, inplace = True)
    return all_articles

def sentiment(text):
    return sia.polarity_scores(text)['compound']

def runSent(df):
    for index, row in df.iterrows():
        if (row['description'] != None):
            sentVal = sentiment(row['description'])
            df.loc[index, 'sentiment'] = sentVal
            sentVal = 0
        else:
            sentVal = sentiment(row['content'])
            df.loc[index, 'sentiment'] = sentVal
            sentVal = 0
            
    df = df[df['sentiment'] != 0]
    return df

df = pd.DataFrame()

for ticker in tickers:
    df = df.append(get_articles(ticker,date),sort=True)

df = runSent(df)

df = df.drop(columns=['articles','source','status','totalResults'])
df = df[['publishedAt', 'title', 'description', 'content', 'company','ticker','sentiment', 'lastPrice']]

jsonresp = df.to_json(orient='records')

print(jsonresp)

