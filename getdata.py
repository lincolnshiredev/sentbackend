import requests
import pandas as pd
import xmltodict

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer # Requires 'pip install vaderSentiment'

sia = SentimentIntensityAnalyzer()

def sentiment(text):
    return sia.polarity_scores(text)['compound']

def flatten_dict(dd, separator='_', prefix=''):
    return { prefix + separator + k if prefix else k : v
             for kk, vv in dd.items()
             for k, v in flatten_dict(vv, separator, kk).items()
             } if isinstance(dd, dict) else { prefix : dd }

def request(ticker):
    news = requests.get(url='https://seekingalpha.com/api/sa/combined/' + ticker + '.xml')
    data = xmltodict.parse(news.text)

    
    
    flattened_doc = [flatten_dict(x) for x in data['rss']['channel']['item']]

    df = pd.DataFrame(flattened_doc)
    
    for index,row in df.iterrows():
        if (row['title']!=None): # The GME dataframe has no content for some articles so this checks for that 
            df.loc[index, 'sentiment'] = sentiment(row['title'])
            df.loc[index, 'symbol' ] = ticker
        else:
            df.loc[index, 'sentiment'] = "0"
            df.loc[index, 'symbol' ] = ticker
    return df



# Microsoft

df1 = request("msft")

# Apple

df2 = request("aapl")

# GameStop

df3 = request("GME")

# Merge 3 Dataframes
df1 = df1.append(df2,sort='false')
df1 = df1.append(df3,sort='false')
#print(df1.head())
df1 = df1.drop(columns=['link','guid_#text','guid_@isPermaLink','media:thumbnail_@url','sa:author_name','sa:picture','sa:stock','sa:stock_sa:company_name','sa:stock_sa:symbol'])

df1 = df1[~df1['sentiment'].isin(['0'])]

jsonresp = df1.to_json(orient='records')
print(jsonresp)
    
    

    



