import urllib.request
import json
import pandas as pd
from pandas.io.json import json_normalize

print('############################### MICROSOFT DATA  ##############################')

#----------------------------Live Data-------------------------------------
input("Press Enter for Microsoft Live Profile Data...") 

microsoft_live_profile = urllib.request.urlopen('https://financialmodelingprep.com/api/v3/company/profile/MSFT')
string_microsoft_live_profile = microsoft_live_profile.read().decode('utf-8')
live_data = json.loads(string_microsoft_live_profile)
normallivejson1 = pd.json_normalize(live_data['profile']) #read the profile node from data and using pandas json_normalize automatically read the columns and values
pd.options.display.max_columns = None # This is to display all the columns so there is no limit if our table is bigger
pd.set_option('display.width', 2000) #Here I am setting the width of the table to 2000 columns
print(normallivejson1[['price','changes','changesPercentage','volAvg','companyName']])


#------------------------------Historical Data-----------------------------
input("Press Enter for Microsoft Historical Data...")

microsoft = urllib.request.urlopen('https://financialmodelingprep.com/api/v3/historical-price-full/MSFT?timeseries=5')
string_microsoft = microsoft.read().decode('utf-8')
#json_microsoft = json.dumps(string_microsoft) 
data = json.loads(string_microsoft) 
normaljson1 = pd.json_normalize(data['historical'])
pd.options.display.max_columns = None
pd.set_option('display.width', 1000)
normaljson1['companyName']='Microsoft Corporation'
print(normaljson1[['date','open','high','low','close','change','change','companyName']])


print('##############################  APPLE DATA   #############################')

#----------------------------Live Data-------------------------------------
input("Press Enter for APPLE Live Profile Data...") 

apple_live_profile = urllib.request.urlopen('https://financialmodelingprep.com/api/v3/company/profile/AAPL')
string_apple_live_profile = apple_live_profile.read().decode('utf-8')
live_data = json.loads(string_apple_live_profile)
normallivejson2 = pd.json_normalize(live_data['profile'])
pd.options.display.max_columns = None
pd.set_option('display.width', 2000)
print(normallivejson2[['price','changes','changesPercentage','volAvg','companyName']])

#------------------------------Historical Data-----------------------------
input("Press Enter for APPLE Historical Data...")

apple = urllib.request.urlopen('https://financialmodelingprep.com/api/v3/historical-price-full/AAPL?timeseries=5')
string_apple = apple.read().decode('utf-8')
#json_apple = json.dumps(string_apple) 
data = json.loads(string_apple) 
normaljson2 = pd.json_normalize(data['historical'])
pd.options.display.max_columns = None
pd.set_option('display.width', 1000)
normaljson2['companyName']='Apple Inc.'
print(normaljson2[['date','open','high','low','close','change','change','companyName']])

print('##############################  GAME DATA   #############################')

#----------------------------Live Data-------------------------------------
input("Press Enter for GAME Live Profile Data...") 

game_live_profile = urllib.request.urlopen('https://financialmodelingprep.com/api/v3/company/profile/GME')
string_game_live_profile = game_live_profile.read().decode('utf-8')
live_data = json.loads(string_game_live_profile)
normallivejson3 = pd.json_normalize(live_data['profile'])
pd.options.display.max_columns = None
pd.set_option('display.width', 2000)
print(normallivejson3[['price','changes','changesPercentage','volAvg','companyName']])

#------------------------------Historical Data-----------------------------
input("Press Enter for GAME Historical Data...")

game = urllib.request.urlopen('https://financialmodelingprep.com/api/v3/historical-price-full/GME?timeseries=5')
string_game = game.read().decode('utf-8')
#json_game = json.dumps(string_game) 
data = json.loads(string_game) 
normaljson3 = pd.json_normalize(data['historical'])
pd.options.display.max_columns = None
pd.set_option('display.width', 1000)
normaljson3['companyName']='Gamestop Corporation'
print(normaljson3[['date','open','high','low','close','change','change','companyName']])
 


print('###############################   Joining Live Tables #############################')

frameslive = [normallivejson1,normallivejson2,normallivejson3]
resultlive=pd.concat(frameslive)
resultlive.reset_index(drop=True, inplace=True)
print(resultlive[['price','changes','changesPercentage','volAvg','companyName']])


print('###############################   Joining Historical Tables  #############################')
frameshistorical = [normaljson1,normaljson2,normaljson3]
resulthistorical=pd.concat(frameshistorical)
resulthistorical.reset_index(drop=True, inplace=True)
print(resulthistorical[['date','open','high','low','close','change','change','companyName']])


input("Press Enter to Exit...")  
