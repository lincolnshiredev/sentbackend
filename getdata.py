# Requires 'pip install vaderSentiment'
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
import pandas as pd
import xmltodict
import requests
import random
import json
import dateparser

sia = SentimentIntensityAnalyzer()

apiKey = ['3ce9e0ab3ce7491b896c2fff0aae03ea', '54b57422e2d14f169dd132ca36c669f2', '6f0e158decfb4262a93248b4c5337616', 'fc0b654bc64a47c0a4d0fa880acbaf6b', '25b072e7437e4aeea6e1eba44d3fce7f',
          '0e2b90f581084acd94162753f5c8ba25', '6c6ba1e5abec480abcfd97889e46ef41', 'e3e321b663fa43f581cc4cfd922ff9a1', '74571be91b5544e38860a4c8baf7bfda', 'efbd8a0c9a2a41fa8d1cc365db79a39a']


def sentiment(text):
    return sia.polarity_scores(text)['compound']


def flatten_dict(dd, separator='_', prefix=''):
    return {prefix + separator + k if prefix else k: v
            for kk, vv in dd.items()
            for k, v in flatten_dict(vv, separator, kk).items()
            } if isinstance(dd, dict) else {prefix: dd}


def relevance(df, ticker):
    for index, row in df.iterrows():
        if((((str(['ticker'])).lower()) in ((str(row['title'])).lower())) or (((str(['companyName'])).lower()) in ((str(row['title'])).lower()))):
            df.loc[index, 'relevence'] = 1
        elif((((str(['ticker'])).lower()) in ((str(row['description'])).lower())) or (((str(['companyName'])).lower()) in ((str(row['description'])).lower()))):
            df.loc[index, 'relevence'] = 0
        else:
            df.loc[index, 'relevence'] = -1  # consider dropping
    return df


def request(ticker, date):

    news = requests.get(
        url='https://seekingalpha.com/api/sa/combined/' + ticker[0] + '.xml')

    news1 = requests.get(url='https://newsapi.org/v2/everything?q=' +
                         ticker[1] + '&sortBy=popularity' + '&from=' + date + '&apiKey=' + apiKey[(random.randint(0, 9))])

    data = xmltodict.parse(news.text)

    flattened_doc = [flatten_dict(x) for x in data['rss']['channel']['item']]
    df = pd.DataFrame(flattened_doc)
    df1 = pd.read_json(json.dumps((news1.json())['articles']))
    # df1 = (pd.read_json(json.dumps((news1.json())['articles'])))
    # print(df1)

    df = df.drop(columns=['guid_#text', 'guid_@isPermaLink', 'media:thumbnail_@url',
                          'sa:picture', 'sa:stock_sa:company_name', 'sa:stock_sa:symbol'])

    for index, row in df1.iterrows():
        df1.loc[index, 'sourceName'] = (
            (((str(row['source']).split("'name': '", 1))[1]).split("'}", 1))[0])

    df.rename(columns={'link': 'url', 'sa:author_name': 'author'})
    df1.rename(columns={'publishedAt': 'pubDate'})

    df1 = df1.drop(columns=['content', 'author', 'source'])

    df = df.append(df1)

    for index, row in df.iterrows():

        df.loc[index, 'ticker'] = ticker[0]
        df1.loc[index, 'companyName'] = ticker[1]

        if (row['title'] != None):
            df.loc[index, 'sentiment'] = sentiment(row['title'])

        else:
            df.loc[index, 'sentiment'] = "0"

    df = df[~df['sentiment'].isin(['0'])]

    df = relevance(df, ticker)

    return df


tickers = [["mfst", "microsoft"], ["aapl", "apple"],
           ["GME", "gamestop"], ["amzn", "amazon"]]

df = pd.DataFrame()

date = (((datetime.now())-timedelta(days=14)).strftime("%Y-%m-%d"))

for ticker in tickers:
    df = df.append(request(ticker, date))

df = df.fillna('')

df['pubDate'] = df['pubDate'].astype(str) + df['publishedAt'].astype(str)

df['link'] = df['link'].astype(str) + df['url'].astype(str)

df = df.drop(columns=['sa:stock', 'urlToImage', 'publishedAt',
                      'sourceName', 'sa:author_name', 'url', 'description'])

# print(dateparser.parse('2020-02-10T19:00:00Z'))

jsonresp = df.to_json(orient='records')
print(jsonresp)
