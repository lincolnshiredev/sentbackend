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
# This code can be deployed to Google Cloud Functions 

def getNews(request):
    # When the a REST request is made to the above API endpoint then this function is ran 
    request_json = request.get_json(silent=True)
    request_args = request.args
    
    ticker: str = ''
       
    if request_json and 'ticker' in request_json:
        ticker = str(request_json['ticker'])
    elif request_args and 'ticker' in request_args:
        ticker = str(request_args['ticker'])
    else:
        ticker: str = 'AAPL'
    # If the request contains a specific ticker then that data is extracted for use
    # Otherwise we default the script to use AAPL to obtain news articles

    newsapi = NewsApiClient(api_key='api key here')
    # Powered by NewsAPI.org

    headers = {'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com",
            'x-rapidapi-key': "api key"}
    # Set out the api keys for use in retrieving news articles articles

    sia = SentimentIntensityAnalyzer()

    date = (datetime.now()).strftime("%Y-%m-%d")
    newsApiDf = pd.DataFrame()
    yahooNewsDf = pd.DataFrame() 

    numberOfArticles:int = 0
    overallSentiment: float = 0.0

    #Get NewsAPI
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
    
    #Finish With NewsApi

    #Get Yahoo News
    querystring = {"category": ticker, "region": "US"}

    yahooNews = requests.get(url='https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-newsfeed',
                        headers=headers, params=querystring)
    # A request for news articles from Yahoo News is made using APIDojo.net

    yahooNewsDf = pd.read_json(json.dumps((yahooNews.json())['items']['result']))
    # The JSON response from the API is converted into a dataframe 

    yahooNewsDf = yahooNewsDf.drop(columns=['uuid', 'main_image','entities', 'ignore_main_image', 'streams',
                          'offnet', 'reference_id', 'is_magazine', 'type', 'author'])
    # Columns that have no use to our application are dropped()

    for index, row in yahooNewsDf.iterrows():
        yahooNewsDf.loc[index, 'sentiment'] = sia.polarity_scores(row['summary'])['compound']
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
    
    for ind,row in yahooNewsDf.iterrows():
        overallSentiment  = overallSentiment+row['sentiment']
        numberOfArticles = numberOfArticles + 1
        # We sum up the sentiment values and count the number of articles in the dataframe

    #Finish with Yahoo News
    
    if (len(newsApiDf) != 0):
        for index, row in newsApiDf.iterrows():
            if (row['description'] != None):
                # If the description column contains data then sentiment analysis is ran on it
                # The result is stored in the dataframe in the sentiment column
                sentVal = sia.polarity_scores(row['description'])['compound']
                newsApiDf.loc[index, 'sentiment'] = sentVal
                sentVal = 0
            else:
                # If the description column does not contain data then sentiment analysis is ran on the content column
                sentVal = sia.polarity_scores(row['content'])['compound']
                newsApiDf.loc[index, 'sentiment'] = sentVal
                sentVal = 0
            if((row['urlToImage'] is None) or (row['urlToImage'] == "null")):
                row['urlToImage'] = "https://images.pexels.com/photos/102720/pexels-photo-102720.jpeg"                 
                # If the column urlToImage doesnt contain a value then a stock image is used
                # Stock image, by: Markus Spiske, hosted on: https://www.pexels.com/
            newsApiDf = newsApiDf[newsApiDf['sentiment'] != 0]
            # Remove any articles that do not have a sentiment score

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

    return jsonresp