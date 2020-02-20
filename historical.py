import urllib.request
import json

#apple data
apple = urllib.request.urlopen('https://financialmodelingprep.com/api/v3/historical-price-full/AAPL?timeseries=5')

input("Press Enter for Apple Historical Data...") 

string_apple = apple.read().decode('utf-8') 

json_apple = json.dumps(string_apple)  

data = json.loads(string_apple) 
print('   date    ','|','  open ','|', ' high   ','|', ' low   ','|', '  close  ','|', ' change ','|', ' volume  ','|', ' ticker') #create the header for the table to show output
for  v in data['historical']: 

    print(v['date'], ' | ', v['open'], ' | ', v['high'], ' | ', v['low'], ' | ', v['close'], ' | ', v['change'], ' | ', v['volume'], ' | ','AAPL') #pring the data from each object

#microsoft data

microsoft = urllib.request.urlopen('https://financialmodelingprep.com/api/v3/historical-price-full/MSFT?timeseries=5')

input("Press Enter for Microsoft Historical Data...")

string_microsoft = microsoft.read().decode('utf-8')

json_microsoft = json.dumps(string_microsoft) 

data = json.loads(string_microsoft) 

print('   date    ','|','  open ','|', ' high   ','|', ' low   ','|', '  close  ','|', ' change ','|', ' volume  ','|', ' ticker')
for  v in data['historical']: 

    print(v['date'], ' | ', v['open'], ' | ', v['high'], ' | ', v['low'], ' | ', v['close'], ' | ', v['change'], ' | ', v['volume'], ' | ','MSFT') #pring the data from each object
   
#gamestop data

gamestop = urllib.request.urlopen('https://financialmodelingprep.com/api/v3/historical-price-full/GME?timeseries=5')

input("Press Enter for Gamestop Corporation Historical Data...")



string_gamestop = gamestop.read().decode('utf-8')



json_gamestop = json.dumps(string_gamestop)

data = json.loads(string_gamestop)

print('   date    ','|','  open ','|', ' high   ','|', ' low   ','|', '  close  ','|', ' change ','|', ' volume  ','|', ' ticker')
for  v in data['historical']:

    print(v['date'], ' | ', v['open'], ' | ', v['high'], ' | ', v['low'], ' | ', v['close'], ' | ', v['change'], ' | ', v['volume'], ' | ','GME')

def apple():
    f= open("apple-historical.txt","w+")

    f.write(json_apple)
    f.close()

def microsoft():
    f= open("microsoft-historical.txt","w+")

    f.write(json_microsoft)
    f.close()

def gamestop():
    f= open("gamestop-historical.txt","w+")

    f.write(json_gamestop)
    f.close()


if __name__== "__main__":
  apple()
  microsoft()
  gamestop()
  
  input("Press Enter to exit...")