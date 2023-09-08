import requests
import json as js
from time import sleep

class WeatherForecast:
    
    # Initialize API
    __BASE_URL = "https://api.weatherbit.io/v2.0/forecast/daily?"
    __API_KEY = "051d187cb45f4da7835e3fcd695dc707"
    
    # Initialize class
    def __init__(self, city_name = 'Nagpur', state_name = 'Maharashtra', days = 7):
        self.city_name = '+'.join(city_name.lower().strip().split())
        self.state_name = '+'.join(state_name.lower().strip().split())
        self.country_code = 'IN'
        self.days = days
        self.response = None
        self.response_code = None
        self.weather_data = list()
        
    # API caller
    def api_caller(self):
        try:
            api_call_url = "{0}city={1}&state={2}&country={3}&key={4}&days={5}".format(self.__BASE_URL, self.city_name, self.state_name, self.country_code, self.__API_KEY, self.days)
            self.response = requests.get(api_call_url)
            sleep(5)
            self.response_code = self.response.status_code
            return self.response_code
        except Exception as msg:
            print("api_caller():", msg)
            return -1
        
    # Check if the API call was successful
    def is_api_call_success(self):
        if self.response_code == 200:
            return True
        elif self.response_code == 204:
            print('Oops! It seems there was an issue with the API call. Please check your input and try again later.')
        return False
    
    # Build a json file from the API response
    def json_file_bulider(self):
        try:
            json_obj = self.response.json()
            with open('weather_data.json', 'w') as file:
                js.dump(json_obj, file, indent = 1, sort_keys = True)
            print("weather_data.json file build successfully")
        except Exception as msg:
            print("json_bulider():", msg)
            
    # Get the weather data
    def get_weather_data(self):
        json_obj = self.response.json()
        prolonged_precip = 0
        prolonged_prob = 0
        heavy_rain_2d = False
        heavy_rain_chance_2d = 0
        precip_2d = 0
        precip_chance_2d = 0
        
        for i in range(self.days):
            date = json_obj['data'][i]['datetime']
            temp = json_obj['data'][i]['temp']
            rh = json_obj['data'][i]['rh']
            precip = json_obj['data'][i]['precip']
            prob = json_obj['data'][i]['pop']
            w_code = json_obj['data'][i]['weather']['code']
            w_desc = json_obj['data'][i]['weather']['description']
            i_code = json_obj['data'][i]['weather']['icon']
            prolonged_precip += precip
            prolonged_prob += prob

            count_2d = 0
            if i < 2:
                precip_2d += precip
                precip_chance_2d += prob
                if w_code in [202, 233, 502, 521, 522]:
                    heavy_rain_2d = True
                    heavy_rain_chance_2d += prob
                    count_2d += 1
                    heavy_rain_chance_2d //= count_2d
            
            di = {
                  "Date":date, 
                  "Temperature":temp, 
                  "Relative Humidity":rh, 
                  "Rainfall":precip, 
                  "Probability of Precipitation":prob,
                  "Weather Description": w_desc
                 }
            self.weather_data.append(di)

        prolonged_prob //= self.days
        precip_chance_2d //= 2
        
        if heavy_rain_2d:
            print("*" * 21, "Heavy Rain Alert", "*" * 21)
            print("Chances of Heavy Rain within the Next 2 Days:", heavy_rain_chance_2d)
            print("Heavy rainfall can impact your fertilizer application.")
            print("*" * 21, "Heavy Rain Alert", "*" * 21)
            return ('Warning', 'Heavy Rain Alert', 'Chances of Heavy Rain within the next two days: %d%% %' % (heavy_rain_chance_2d))

        elif prolonged_precip > 12.7 and prolonged_prob >= 50:
            print("*" * 21, "Prolonged Rainfall Alert", "*" * 21)
            print("Warning: Prolonged rainfall of more than 12.7 mm may impact your fertilizer.")
            print("*" * 21, "Prolonged Rainfall Alert", "*" * 21)
            return ('Warning', 'Prolonged Rainfall Alert', 'Expect prolonged rainfall of over 12.7 mm in the next seven days with a %d%% chance.' % (prolonged_prob))

        else:
            print("-" * 80)
            print("Rainfall Forecast for the Next 2 Days (including today):", precip_2d)
            print("Probability of Rain for the Next 2 Days (including today):", precip_chance_2d)
            print()
            return ('Message', 'Precipitation Forecast', 'Rainfall forecast for the next 2 days (including today) is %.2f mm with a %d%% chance.' % (precip_2d, precip_chance_2d))


        