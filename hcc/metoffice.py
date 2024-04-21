
import requests
import json
import dotenv
from typing import Dict, Any, Optional
import pandas as pd
import os

# call Met Office weatherhub API to retrieve site specific weather data
# https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point

def _decode_response(response: any) -> pd.DataFrame:
    resp = json.loads(response)
    fcst = resp['features'][0]['properties']['timeSeries']

    import pandas as pd
    df = pd.DataFrame(fcst)
    
    wc = df['significantWeatherCode'].map(str)
    df['description'] = [weather_codes[w] for w in wc]
    df['icon'] = [weather_code_icons[w] for w in wc]
    # df.head()
    return(df)

    # from datetime import datetime
    # datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # return(df)

def get_api_key() -> str:
    """Get the Met Office API key from the environment variable or .env file"""
    key = 'MET-OFFICE-API-KEY'

    api_key = None
    try:
        api_key = os.environ[key]
    except KeyError:
        pass
    
    if api_key is None:
        try:
            vars = dotenv.dotenv_values('.env')
            api_key = vars[key]
        except KeyError:
            pass

    if api_key is None:
        raise ValueError("MET-OFFICE-API-KEY key not found in environment variable or .env file")


    return(api_key)

def get_weather(lat:float, lon:float, type:Optional[str] = None, api_key:Optional[str] = None) -> pd.DataFrame:
    """Get weather forecast data from the Met Office API

    :param: lat: latitude
    
    :param: lon: longitude

    :param: type: type of forecast, can be one of "hourly", "three-hourly" or "daily". Default is "hourly".

    :param: api_key: Met Office API key. If not provided, it will be read from the environment variable or .env file
    """
    if type is None:
        type = "three-hourly"

    if type not in ["hourly", "three-hourly", "daily"]:
        raise ValueError("type must be one of 'hourly' or 'daily'")

    if api_key is None:
        api_key = get_api_key()
    
    resp = _call_weather_api(lat, lon, type, api_key = api_key)
    df = _decode_response(resp)
    return(df)

def _call_weather_api(lat:float, lon:float, type:Optional[str] = None, api_key:Optional[str] = None) -> Dict[str, Any]:
    """Get weather forecast data from the Met Office API

    :return: a json object with the weather forecast data

    >>> call_weather_api()
    """

    if type is None:
        type = "hourly"

    params = {
        'excludeParameterMetadata': True,
        # 'includeLocationName': 'Hampton Hill',
        'latitude': lat,
        'longitude': lon
    }

    if api_key is None:
        api_key = get_api_key()

    headers = {
        'accept': "application/json", 
        'apikey': api_key
        }

    api_url = 'https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point'
    api_url = api_url + '/' + type

    try:
        response = requests.get(api_url, headers = headers, params = params)
        success = True
    except Exception as e:
        print('Failed to retrieve data:', e)
        print('status code:', response.status_code)
        
        # stop the program
        success = False

    
    resp = response.text
    return(resp)


weather_codes = {
'NA':	'Not available',
'-1':	'Trace rain',
'0':	'Clear night',
'1':	'Sunny day',
'2':	'Partly cloudy (night)',
'3':	'Partly cloudy (day)',
'4':	'Not used',
'5':	'Mist',
'6':	'Fog',
'7':	'Cloudy',
'8':	'Overcast',
'9':	'Light rain shower (night)',
'10':	'Light rain shower (day)',
'11':	'Drizzle',
'12':	'Light rain',
'13':	'Heavy rain shower (night)',
'14':	'Heavy rain shower (day)',
'15':	'Heavy rain',
'16':	'Sleet shower (night)',
'17':	'Sleet shower (day)',
'18':	'Sleet',
'19':	'Hail shower (night)',
'20':	'Hail shower (day)',
'21':	'Hail',
'22':	'Light snow shower (night)',
'23':	'Light snow shower (day)',
'24':	'Light snow',
'25':	'Heavy snow shower (night)',
'26':	'Heavy snow shower (day)',
'27':	'Heavy snow',
'28':	'Thunder shower (night)',
'29':	'Thunder shower (day)',
'30':	'Thunder'
}

weather_code_icons = {
'NA':	'',
'-1':	'wi-day-rain-mix',
'0':	'wi-night-clear',
'1':	'wi-day-sunny',
'2':	'wi-night-partly-cloudy',
'3':	'wi-day-cloudy',
'4':	'',
'5':	'wi-day-fog',
'6':	'wi-day-fog',
'7':	'wi-day-cloudy',
'8':	'wi-day-sunny-overcast',
'9':	'wi-night-rain',
'10':	'wi-day-rain',
'11':	'wi-day-sleet',
'12':	'wi-day-rain',
'13':	'wi-night-storm-showers',
'14':	'wi-day-storm-showers',
'15':	'wi-day-showers',
'16':	'wi-night-sleet-storm',
'17':	'wi-day-sleet-storm',
'18':	'wi-day-sleet',
'19':	'wi-night-hail',
'20':	'wi-day-hail',
'21':	'wi-day-hail',
'22':	'wi-night-snow',
'23':	'wi-day-snow',
'24':	'wi-day-snow',
'25':	'wi-night-snow-thunderstorm',
'26':	'wi-day-snow-thunderstorm',
'27':	'wi-day-snow-thunderstorm',
'28':	'wi-night-thunderstorm',
'29':	'wi-day-thunderstorm',
'30':	'wi-day-thunderstorm'
}