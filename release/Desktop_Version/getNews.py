from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
from datetime import datetime
from newsapi import NewsApiClient
import pandas as pd
import dateparser
import requests
import string
import time
import json

sia = SentimentIntensityAnalyzer()

date = (datetime.now()).strftime("%Y-%m-%d")

newsapi = NewsApiClient(api_key='d1303aa27f3840d9a0c5da1cccfc171b')
# Powered by NewsAPI.org

headers = {'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com",
           'x-rapidapi-key': "8d02ef92a9mshbe032b4fec7a9bfp15eb07jsn6fc9e511caff"}
# Set out the api keys for use in retrieving news articles articles

def getNewsApiArticles(ticker: str, date):
    #  This function retrievs the news articles from NewsAPI.org and them puts them into a dataframe 
    
    print('Getting Artices from News API')
    newsApiDf = newsapi.get_everything(q=ticker,
                                          from_param=date,
                                          language='en',
                                          page=1)
    # We request news articles for the specified company from NewsAPI.org 
    # If successful then we get a status code of 200 along with the JSON data  

    newsApiDf = pd.DataFrame(newsApiDf)
    # We convert the JSON response from NewsAPI.org into a datraframe allowing for easy manipulation of the data
    
    newsApiDf = pd.concat([newsApiDf.drop(
        ['articles'], axis=1), newsApiDf['articles'].apply(pd.Series)], axis=1)
    
    newsApiDf.drop_duplicates(subset="title",
                                 keep=False, inplace=True)
    # Any duplicate articles are dropped from the dataframe 

    for index, row in newsApiDf.iterrows():
        time1 =  dateparser.parse(str(row['publishedAt'])) 
        time1 = int(time.mktime(time1.timetuple()))
        time1 = time.gmtime(time1)
        time1 = time.strftime("%Y-%m-%d", time1)
        newsApiDf.loc[index, 'publishedAt'] = time1
        # The date of publication is standardised
    
    for index, row in newsApiDf.iterrows():
        newsApiDf.loc[index, 'sourceName'] = (
            (((str(row['source']).split("'name': '", 1))[1]).split("'}", 1))[0])
    # To make it easier to display the source name on the front end we extract it so 
    # only the name of the articles source is used and not the additional informatrion that the column contains
        
    print("Successfully got articles from News API")

    return newsApiDf


def getYahooNewsArticles(ticker: str):
    # This function will onbtain news atricles from Yahoo News, using APIDojo.net
    # Convert the JSON response to a datframe 
    # Run sentiment on one of the columns and then standardise the columns so the 
    # dataframe can be appended to the dataframe from our other news source 
    
    print('Getting Articles from Yahoo')
    querystring = {"category": ticker, "region": "US"}

    yahooNews = requests.get(url='https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-newsfeed',
                        headers=headers, params=querystring)
    # A request for news articles from Yahoo News is made 

    yahooNewsDf = pd.read_json(json.dumps((yahooNews.json())['items']['result']))
    # The JSON response from the API is converted into a dataframe 
    
    yahooNewsDf = yahooNewsDf.drop(columns=['uuid', 'main_image','entities', 'ignore_main_image', 'streams',
                          'offnet', 'reference_id', 'is_magazine', 'type', 'author'])
    # Columns that have no use to our application are dropped

    for index, row in yahooNewsDf.iterrows():
        yahooNewsDf.loc[index, 'sentiment'] = sentiment(row['summary'])
        # Sentiment analysis is ran on the summary column, this contains the most data so should give the most accurate sentiment score 

        yahooNewsDf.loc[index, 'urlToImage'] = "https://images.pexels.com/photos/102720/pexels-photo-102720.jpeg" 
        # Example stock image, by: Markus Spiske, hosted on: https://www.pexels.com/
    
    yahooNewsDf = yahooNewsDf[yahooNewsDf['sentiment'] != 0]
    # Drop any news articles that havent obtained a sentiment value
        
    yahooNewsDf.rename(columns={'published_at': 'publishedAt',
                        'summary': 'description', 'link': 'url','publisher':'sourceName'}, inplace=True)
    # We standardised the column names with the other dataframe so we can append the two
    
    yahooNewsDf = yahooNewsDf.drop(columns=['content','description'])
    # We drop content and description as they have been used for sentiment analysis but arent needed on the front end 
    
    print("successfully retrieved articles from yahoo and performed sentiment analysis")
    return yahooNewsDf


def sentiment(text):
    # This uses the vader sentiment rule based sentiment analysis tool to give the articles a sentiment 
    return sia.polarity_scores(text)['compound']


def runSent(dataFrame):
    print('Perfoming Sentiment Analysis on news api')
    
    for index, row in dataFrame.iterrows():
        if (row['description'] != None):
            # If the description column contains data then sentiment analysis is ran on it
            # The result is stored in the dataframe in the sentiment column
            sentVal = sentiment(row['description'])
            dataFrame.loc[index, 'sentiment'] = sentVal
            sentVal = 0
        else:
            # If the description column does not contain data then sentiment analysis is ran on the content column
            sentVal = sentiment(row['content'])
            dataFrame.loc[index, 'sentiment'] = sentVal
            sentVal = 0

    dataFrame = dataFrame[dataFrame['sentiment'] != 0]
    # Remove any articles that do not have a sentiment score
    
    print('Sentiment Analysis Complete on news api')
    return dataFrame


newsApiDf = pd.DataFrame()
yahooNewsDf = pd.DataFrame() 

numberOfArticles: int = 0
overallSentiment: float = 0.0

tickers = ["aapl"]

for ticker in tickers:
    newsApiDf = newsApiDf.append(getNewsApiArticles(ticker, date), sort=True)
    yahooNewsDf = yahooNewsDf.append(getYahooNewsArticles(ticker))
    # We call the two obtain news article functions and put them into a both into separate dataframes 

for ind,row in yahooNewsDf.iterrows():
    overallSentiment  = overallSentiment+row['sentiment']
    numberOfArticles = numberOfArticles + 1
    # We sum up the sentiment values and count the number of articles in the dataframe

if (len(newsApiDf) != 0):
   
    newsApiDf = runSent(newsApiDf)
    
    for ind, row in newsApiDf.iterrows():
        overallSentiment = overallSentiment+row['sentiment']
        numberOfArticles = numberOfArticles + 1
    
    newsApiDf = newsApiDf.drop(columns=['content','description','status','totalResults','author','source'])
    
    newsApiDf = newsApiDf.append(yahooNewsDf,sort=True)
    # Now that two two dataframes have the same column names we can append them together

    avgSentiment:float = overallSentiment/numberOfArticles
    # The average sentiment value is calculated based on the sum of sentiment values from the news articles and then 
    # number of articles that are available to us 
    
    valuesDict ={"numberOfArticles":numberOfArticles,"overallSentiment":overallSentiment,"avgSentiment": ("{0:.2f}".format(avgSentiment))}
    # We create a dictionary to format the data on the overall sentiment values, this allows us to convert it to JSON 
    
    newsApiDict = newsApiDf.to_dict(orient='records')
    # The news articles are orientated as records so that they are formatted better for the front end & converted to a dictionary
    
    newsApiDf.drop

    newsArticlesDict = {'articles ':newsApiDict,'additionalData':valuesDict}
    # We create a dictionary to hold the articles and the overall sentiment values
    
    jsonresp = json.dumps(newsArticlesDict, default=str)
    # The dictionary previously created is converted to JSON so it can be used on the front end
else:

    print('no results for news api')
    
    avgSentiment:float = overallSentiment/numberOfArticles
    # The average sentiment value is calculated based on the sum of sentiment values from the news articles and then 
    # number of articles that are available to us 
    
    valuesDict ={"numberOfArticles":numberOfArticles,"overallSentiment":overallSentiment,"avgSentiment": ("{0:.2f}".format(avgSentiment))}
    # We create a dictionary to format the data on the overall sentiment values, this allows us to convert it to JSON 
    
    yahooNewsDict = yahooNewsDf.to_dict(orient='records')
    # The news articles are orientated as records so that they are formatted better for the front end 7 converted to a dictionary
    
    newsArticlesDict = {'articles':yahooNewsDict,'additionalData':valuesDict}
    # We create a dictionary to hold the articles and the overall sentiment values
    
    jsonresp = json.dumps(newsArticlesDict, default=str)
    # The dictionary previously created is converted to JSON so it can be used on the front end

print(jsonresp)