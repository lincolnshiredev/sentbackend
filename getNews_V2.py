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

headers = {'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com", 
'x-rapidapi-key': "8d02ef92a9mshbe032b4fec7a9bfp15eb07jsn6fc9e511caff"}

tickers = [["mfst", "microsoft"], ["aapl", "apple"],
           ["GME", "gamestop"], ["amzn", "amazon"]]

def get_articles(ticker,date):

    all_articles = newsapi.get_everything(q=ticker[0],
                                      from_param= date,
                                      language='en',
                                      page=1)

    all_articles = pd.DataFrame(all_articles)
    all_articles = pd.concat([all_articles.drop(['articles'], axis=1), all_articles['articles'].apply(pd.Series)], axis=1)
    all_articles["ticker"] = ticker[0]
    all_articles["company"] = ticker[1]
    all_articles.drop_duplicates(subset ="title", 
                     keep = False, inplace = True)
    return all_articles

def request(ticker):

    querystring = {"category": ticker[0], "region": "US"}

    news = requests.get(url='https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-newsfeed',
                        headers=headers, params=querystring)

    df = pd.read_json(json.dumps((news.json())['items']['result']))
    df = df.drop(columns=['uuid', 'main_image', 'entities', 'ignore_main_image', 'streams',
                          'offnet', 'reference_id', 'is_magazine', 'type', 'publisher', 'author'])

    df['summary'] = df['summary'].str.lower()
    df['content'] = df['content'].str.lower()

    df['occuranceSum'] = df['summary'].str.count(ticker[0]) + df['summary'].str.count(
        ticker[1]) + df['title'].str.lower().str.count(ticker[0]) + df['title'].str.lower().str.count(ticker[1])

    df['occuranceCont'] = df['content'].str.count(ticker[0]) + df['content'].str.count(
        ticker[1]) + df['title'].str.lower().str.count(ticker[0]) + df['title'].str.lower().str.count(ticker[1])

    df['occuranceSum'].fillna(0, inplace=True)
    df['occuranceCont'].fillna(0, inplace=True)
    df['occurnanceTot'] = df['occuranceSum'] + df['occuranceCont']
    df = df[df['occurnanceTot'] != 0]

    for index, row in df.iterrows():

        df.loc[index, 'ticker'] = ticker[0]
        df.loc[index, 'company'] = ticker[1]
        df.loc[index, 'sentiment'] = sentiment(row['summary'])
       
    df = df[df['sentiment'] != 0]

    return df

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
df2 = pd.DataFrame()

for ticker in tickers:
    df = df.append(get_articles(ticker,date),sort=True)
    df2 = df2.append(request(ticker))

df = runSent(df)

df = df.drop(columns=['articles','source','status','totalResults'])
df = df[['publishedAt', 'title', 'description','url', 'company','ticker','sentiment']]
df2.rename(columns = {'published_at':'publishedAt', 'summary':'description','link':'url'}, inplace = True) 
df2 = df2[['publishedAt','title','description','url','company','ticker','sentiment']]
df = df.append(df2,sort=True)
df = df[['publishedAt', 'title', 'description','url', 'company','ticker','sentiment']]

jsonresp = df.to_json(orient='records')
#df.to_json(r'data1.json', orient='records')
print(jsonresp)

