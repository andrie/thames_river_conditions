"""
Created on Fri May  8 11:25:31 2020
@author: User
"""

import pandas as pd
import requests

def get_stations(
        parameter_name = None,
        parameter = None,
        qualifier = None,
        label = None,
        town = None,
        catchment_name = None,
        river_name = None,
        station_reference = None,
        rloi_id = None,
        search = None,
        lat = None,
        long = None,
        d = None,
        type = None,
        status = None
    ):
    """ Get details of river monitoring stations from EA API

        Each argument limits return results as follows:

        Arguments:
    
            :parameter_name: 
                Return only those stations which measure parameters with the
                given name, for example Water Level or Flow.
            :parameter: 
                Return only those stations which measure parameters with the
                given short form name, for example level or flow.
            :qualifier: 
                Return only those stations which measure parameters with
                qualifier. Useful qualifiers are Stage and Downstream Stage (for
                stations such as weirs which measure levels at two locations),
                Groundwater for groundwater levels as opposed to river levels
                and Tidal Level for tidal levels.
            :label: 
                Return only those stations whose label is exactly as given.
            :town: 
                Return only those stations whose town is as given. Not all
                stations have an associated town.
            :catchment_name: 
                Return only those stations whose catchment name is exactly as
                given. Not all stations have an associated catchment area.
            :river_name: 
                Return only those stations whose river name is exactly as given.
                Not all stations have an associated river name.
            :station_reference: 
                Return only those stations whose reference identifier is as
                given. The station reference is an internal identifier used by
                the Environment Agency.
            :rloi_id: 
                Return only the station (if there is one) whose RLOIid (River
                Levels on the Internet identifier) matches.
            :search: 
                Return only those stations whose label contains the given value.
            :lat: 
                Return those stations whose location falls within d km of the
                given latitude/longitude (in WGS84 coordinates), this may be
                approximated by a bounding box.
            :long: 
                Return those stations whose location falls within d km of the
                given latitude/longitude (in WGS84 coordinates), this may be
                approximated by a bounding box.
            :d: 
                Return those stations whose location falls within d km of the
                given latitude/longitude (in WGS84 coordinates), this may be
                approximated by a bounding box.
            :type: 
                Return only those stations of the given type, where type can be
                one of "SingleLevel", "MultiTraceLevel", "Coastal",
                "Groundwater" or "Meteorological"
            :status: 
                Return only those stations with the given status. Can be one of
                "Active", "Closed" or "Suspended".

      :return: a pandas data frame of river monitoring stations
      >>> get_stations()
  """

  
    api_url = "https://environment.data.gov.uk/flood-monitoring/id/stations"
 
    # Build dictionary of query params from arguments
    params = {'parameterName': parameter_name,
    'parameter': parameter,
    'qualifier': qualifier,
    'label': label,
    'town': town,
    'catchmentName': catchment_name,
    'riverName': river_name,
    'stationReference': station_reference,
    'RLOIid': rloi_id,
    'search': search,
    'lat': lat,
    'long': long,
    'dist': d,
    'type': type,
    'status': status
    }
    
    # Get data about stations from the EA API
    response = requests.get(api_url, 
                            params = params)

    # Extract JSON data from the response
    data = response.json()

    # Load data to a data frame
    stations = pd.DataFrame(data["items"])

    return(stations)



def get_measures(parameter_name = None,
                 parameter = None,
                 qualifier = None,
                 station_reference = None,
                 station = None,
                 search = None):
    """Get details of measures available from river monitoring stations on the EA API

        :param parameter_name: 
            Return only measures for parameters with the given name, for example
            Water Level or Flow.
       :param parameter:
            Return only measures for parameters with the given short form name,
            for example level or flow.
       :param qualifier: 
            Return only those measures with qualifier. Useful qualifiers are
            Stage and Downstream Stage (for stations such as weirs which measure
            levels at two locations), Groundwater for groundwater levels as
            opposed to river levels and Tidal Level for tidal levels.
       :param station_reference: 
            Return only those measures which are available from the station with
            the given reference identifier.
       :param station: 
            Return only those measures which are available from the station with
            the given URI.
       :param search: 
            Return only those measures whose label contains the given value.

       :return: a pandas data frame of river monitoring measures

       >>> get_measures()
    """
    api_url = "http://environment.data.gov.uk/flood-monitoring/id/measures"
    
     # Build dictionary of query params from arguments
    params = {'parameterName': parameter_name,
    'parameter': parameter,
    'qualifier': qualifier,
    'stationReference': station_reference,
    'station': station,
    'search': search
    }
    
    # Get data about measures from the EA API
    response = requests.get(api_url, 
                            params)

    # Extract JSON data from the response
    data = response.json()

    # Load data to a data frame
    measures = pd.DataFrame(data["items"])

    return(measures)
    

def get_readings_for_measure(measure_id, 
                             limit = None,
                             date = None, 
                             startdate = None, 
                             enddate = None,
                             since = None, 
                             latest = False,
                             today = False, 
                             sorted = True):
    """ Gets readings for a given measure from the EA river monitoring API
      :param measure_id:
            EA API measure id
      :param limit:
            Maximum number of records to return. Defaults to 500. Max 10000.
      :param date:
            Return all the readings taken on the specified day.
      :param startdate:
            Return the readings taken on the specified range of days. Date
            format 2020-02-17.
      :param enddate:
            Return the readings taken on the specified range of days. Date
            format 2020-02-17.
      :param since:
            Return the readings taken since the given date time (not inclusive),
            up to the specified limit. If no limit is given then a default limit
            of 500 will be used. Typically when tracking a particular
            measurement then use the dateTime of the last retrieved value as the
            since parameter to find any new readings. Will accept a simple date
            value such as 2016-09-07 which will be interpreted as
            2016-09-07T:00:00:00Z. The latter (with timestamp) is also accepted.
      :param latest:
            Return only the latest reading.
      :param today:
            Return only all readings from today.
      :param sorted:
            Order the array of returned readings into descending order by date,
            this done before the limits is applied thus enabling you to fetch
            the most recent n readings.
      
      :return: a pandas data frame of readings for the measure
      >>> get_readings_for_measure('http://environment.data.gov.uk/flood-monitoring/id/measures/L0215-level-stage-i-15_min-m')
  """
    # Set True/False argument to blank or None so handled correctly in params to requests.get
    if latest:
        latest = ''
    else:
        latest = None
        
    if today:
        today = ''
    else:
        today = None
  
    if sorted:
        sorted = ''
    else:
        sorted = None
    
    # Build dictionary of query params from arguments
    params = {'_limit': limit,
    'date': date,
    'startdate': startdate,
    'enddate': enddate,
    'since': since, 
    'latest': latest,
    'today': today,
    '_sorted': sorted
    }
  
    api_url = measure_id + "/readings"
    
    # Get data about readings from the EA API
    response = requests.get(api_url, 
                            params)

    # Extract JSON data from the response
    data = response.json()

    # Load data to a data frame
    readings = pd.DataFrame(data["items"])

    return(readings)
