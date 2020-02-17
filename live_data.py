import urllib.request
import json


#Apple Live Data - Profile
input("Press Enter for Apple Live Profile Data...") 

apple_live_profile = urllib.request.urlopen('https://financialmodelingprep.com/api/v3/company/profile/MSFT')
string_apple_live_profile = apple_live_profile.read().decode('utf-8')

live_data = json.loads(string_apple_live_profile)

print('price','|','volAvg ','|', ' changes ','|', 'changePercentage')


print(live_data['profile']['price'], '|',live_data['profile']['volAvg'],'|', live_data['profile']['changes'],'|', live_data['profile']['changesPercentage'])

input("Press Enter to Exit...")
