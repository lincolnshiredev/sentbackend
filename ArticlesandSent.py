import requests
import json
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer # Requires 'pip install vaderSentiment'

sia = SentimentIntensityAnalyzer()

def sentiment(text):
    return sia.polarity_scores(text)['compound']

def request(ticker,date,sort):
    news = requests.get(url='https://newsapi.org/v2/everything?q="' + ticker + '"&from='+ date +'&sortBy=' + sort + '&apiKey=54b57422e2d14f169dd132ca36c669f2')
    foo = news.json()
    df = pd.read_json(json.dumps(foo['articles']))
    
    for index,row in df.iterrows():
        if (row['content']!=None): # The GME dataframe has no content for some articles so this checks for that 
            df.loc[index, 'sentiment'] = sentiment(row['description'])
            df.loc[index, 'symbol' ] = ticker
        else:
            df.loc[index, 'sentiment'] = "0"
            df.loc[index, 'symbol' ] = ticker
    return df

# Microsoft

df1 = request("msft","2020-02-11","popularity")

# Apple

df2 = request("aapl","2020-02-11","popularity")

# GameStop

df3 = request("GME","2020-02-11","popularity")

# Merge 3 Dataframes
df1 = df1.append(df2)
df1 = df1.append(df3)
#print(df1.head())
df1 = df1.drop(columns=['urlToImage','source','author','content'])
jsonresp = df1.to_json(orient='records')
print(jsonresp)