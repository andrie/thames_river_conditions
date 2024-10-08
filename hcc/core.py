
from time import strftime

import hcc.ea_rivers as ea_rivers
import plotly.express as px
from functools import lru_cache
import time
from datetime import datetime, timedelta

import pandas as pd
import re

from typing import Any, Tuple

import hcc.ea_rivers as ea_rivers



# cache some functions

@lru_cache()
def get_ea_rivers(
    river_name: str, 
    parameter: str,
    status:str = "Active", 
    time_hash: Any = None):
    """
    Get the stations for a river from the EA API

    Parameters
    ----------
    river_name : str
        Name of the river
    parameter : str
        The parameter to search for, either "level" or "flow"
    status : str, optional
        The status of the station, by default "Active"
    time_hash : Any, optional
        Used internally to cache the result, by default None
    """
    del time_hash  # to emphasize we don't use it and to shut pylint up
    return ea_rivers.get_stations(river_name = river_name, 
        parameter=parameter, status=status)

@lru_cache()
def get_ea_measures(station, parameter = "level", time_hash=None):
    del time_hash  # to emphasize we don't use it and to shut pylint up
    return ea_rivers.get_measures(station = station, parameter = parameter)


def time_hash(seconds=3600):
    """Return the same value within `seconds` time period"""
    return round(time.time() / seconds)


# wrapper around the EA get_stations function
def get_thames_levels(river_name = "River Thames"):
    return get_ea_rivers(river_name, "level", time_hash=time_hash())


# wrapper around the EA get_stations function
def get_thames_flow():
    return get_ea_rivers("River Thames", "flow", time_hash=time_hash())


# Lookup a station name from a search string



def lookup_thames_station_name(station_search, river_name = "River Thames"):
    """Look up a station name from a search string
    """
    stations = get_thames_levels(river_name)
    idx = stations["label"].str.contains(station_search, na = False)
    station_name = stations.loc[idx, ["label"]].values[0][0]
    return station_name

# Lookup the measure URL from the station name
def lookup_thames_station_url(station_name, river_name = "River Thames"):
    stations = get_thames_levels(river_name)
    idx = stations["label"].str.contains(station_name, na = False)
    return stations.loc[idx, "@id"].values[0]


def get_thames_metric(station_search, position = "upstream", parameter = "level", river_name = "River Thames", since = None, limit = None):
    """ Searches for the station name, then plot the upstream or downstream flow

    Parameters
    ----------

        station_search {str} -- Name of the station to search for

        position {str} -- Either "upstream" or "downstream"

        parameter {str} -- Either "level" or "flow"

    Returns:
        Pandas dataframe
    """

    if position == "upstream":
        measure = 0
    else:
        measure = 1
    
    station_name = lookup_thames_station_name(station_search, river_name = river_name)
    found = lookup_thames_station_url(station_name, river_name = river_name)
    measures = get_ea_measures(station = found, parameter = parameter).loc[:, ["@id", "label", "notation"]]

    s1 = measures["@id"].values[measure]
    dat = ea_rivers.get_readings_for_measure(s1, limit = limit, since = since)
    # print(dat.ndim)
    if len(dat) == 0:
        if since is None:
            # seven days earlier:
            since = pd.Timestamp(strftime("%Y-%m-%d %H:%M:%S", gmtime(time() - 7*24*3600)))

        # Get current time
        now = datetime.now()

        # Generate time intervals of 15 minutes for the last week
        time_intervals = [now - timedelta(minutes=15 * i) for i in range(int(7 * 24 * 60 / 15))][::-1]

        # Create DataFrame
        dat = pd.DataFrame({
            'dateTime': time_intervals,
            'value': [None] * len(time_intervals)
        })
    return dat


# Create a plotly plot of either levels or flow
def plot_thames_level(station_search, position = "upstream", parameter = "level", 
    river_name = "River Thames",
    since = None,
    limit = None,
    plot_type = "plotly"):
    """ Searches for the station name, then plot the upstream or downstream flow

    Arguments:

        station_search {str} -- Name of the station to search for

        position {str} -- Either "upstream" or "downstream"

        paramater {str} -- Either "level" or "flow"

    Returns:
        Plotly figure object
    """

    station_name = lookup_thames_station_name(station_search, river_name = river_name)
    s1msr = get_thames_metric(station_name, position = position, 
        parameter = parameter, river_name = river_name, since = since, limit = limit)

    if parameter == "level":
        title = f"{station_name} {position} river level"
        value_label = "River level (m AOD)"
    else:
        title = f"{station_name} {position} river flow"
        value_label = "River flow (m3/s)"

    # Plot the river level
    if plot_type == "plotly":
        fig = px.line(
            s1msr, x="dateTime", y="value", 
            title = title,
            labels = {"dateTime": "Date", "value": f"{value_label}"}
        )
        fig.update_layout(
            autosize=True,
            # width=500,
            # height=500,
        )

        return fig
    else:
        # create plot using matplotlib
        # convert the dateTime column to a datetime object
        s1msr["dateTime"] = pd.to_datetime(s1msr["dateTime"])
        import matplotlib.pyplot as plt
        # create plot using matplotlib
        fig, ax = plt.subplots()
        ax.plot(s1msr["dateTime"], s1msr["value"])
        ax.set_title(title)
        ax.set_xlabel("Date")
        ax.set_ylabel(value_label)
        # ax.locator_params(axis='x', nbins=6)
        ax.xaxis.set_major_locator(plt.MaxNLocator(3))
        return ax

        





        return fig

        # fig = plt.figure()
        # fig = plt.plot(s1msr["dateTime"], s1msr["value"])
        # fig.set_title(title)
        # fig.set_xlabel("Date")
        # fig.set_ylabel(value_label)
        # fig.locator_params(axis='x', nbins=6)
        # fig.xaxis.set_major_locator(plt.MaxNLocator(3))


def find_local(x):
    local = []
    for r in x:
        # print(r)
        if re.search("Walton|Shepperton|Molesey|Teddington|Kingston|Sunbury", r):
            local.append('Local')
        else:
            local.append('No')
    return local

