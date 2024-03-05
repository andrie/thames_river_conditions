
import requests
import json
import dotenv
from typing import Dict, Any, Optional
import pandas as pd
# import os

# call Met Office weatherhub API to retrieve site specific weather data
# https://api-metoffice.apiconnect.ibmcloud.com/v0

def _decode_response(response: any) -> pd.DataFrame:
    # resp = json.loads(response.text)
    resp = json.loads(response)
    fcst = resp['features'][0]['properties']['timeSeries']


    # loop over fc1 to extract time and temperature
    for i in range(0, 24):
        # print(i)
        print(fcst[i]['time'], fcst[i]['screenTemperature'])

    # convert fc1 to pandas dataframe
    import pandas as pd
    df = pd.DataFrame(fcst)
    df.head()
    return(df)

    from datetime import datetime
    datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return(df)

def get_weather(lat:float, lon:float, type:Optional[str] = None) -> pd.DataFrame:
    """Get weather forecast data from the Met Office API

    :param: lat: latitude
    
    :param: lon: longitude

    :param: type: type of forecast, can be one of "hourly" or "daily". Default is "hourly".
    """
    if type is None:
        type = "hourly"

    if type not in ["hourly", "daily"]:
        raise ValueError("type must be one of 'hourly' or 'daily'")
    resp = _call_weather_api(lat, lon, type)
    df = _decode_response(resp)
    return(df)

def _call_weather_api(lat:float, lon:float, type:Optional[str] = None) -> Dict[str, Any]:
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

    vars = dotenv.dotenv_values('.env')

    headers = {
        'accept': "application/json", 
        # MET-OFFICE-ID=b8c778e0d9587cb9bdb57c9d0ba66e92
        # MET-OFFICE-SECRET=97d660e89a304af1f0deae208b659aba
        'x-ibm-client-id'     : vars['MET-OFFICE-ID'],
        'x-ibm-client-secret' : vars['MET-OFFICE-SECRET']
        }

    api_url = 'https://api-metoffice.apiconnect.ibmcloud.com/v0/forecasts/point/hourly'
    # api_url = 'https://api-metoffice.apiconnect.ibmcloud.com/v0/forecasts/point/daily'
    response = requests.get(api_url, headers = headers, params = params)
    
    # check if response is valid
    if response.status_code != 200:
        print('Failed to retrieve data:', response.status_code)
        return None

    # fcst = decode_response(response)
    resp = response.text
    return(resp)