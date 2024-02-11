
from time import strftime

import ea_rivers
import plotly.express as px
from functools import lru_cache
import time


import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

import pytz
import astral
from astral.sun import sun



# cache some functions

@lru_cache()
def get_ea_rivers(river_name, parameter, status="Active", time_hash=None):
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

    Arguments:

        station_search {str} -- Name of the station to search for

        position {str} -- Either "upstream" or "downstream"

        paramater {str} -- Either "level" or "flow"

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
    s1msr = ea_rivers.get_readings_for_measure(s1, limit = limit, since = since)
    return s1msr


# Create a plotly plot of either levels or flow
def plot_thames_level(station_search, position = "upstream", parameter = "level", 
    river_name = "River Thames",
    plot_type = "plotly"):
    """ Searches for the station name, then plot the upstream or downstream flow

    Arguments:

        station_search {str} -- Name of the station to search for

        position {str} -- Either "upstream" or "downstream"

        paramater {str} -- Either "level" or "flow"

    Returns:
        Plotly figure object
    """

    # if position == "upstream":
    #     measure = 0
    # else:
    #     measure = 1
    
    station_name = lookup_thames_station_name(station_search, river_name = river_name)
    # found = lookup_thames_station_url(station_name, river_name = river_name)
    # measures = get_ea_measures(station = found, parameter = parameter).loc[:, ["@id", "label", "notation"]]

    # s1 = measures["@id"].values[measure]
    # s1msr = ea_rivers.get_readings_for_measure(s1)


    s1msr = get_thames_metric(station_name, position = position, 
        parameter = parameter, river_name = river_name)

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


# Scrap the gov.uk for river thames restrictions and closures
def scrape_river_closures():
    url = 'https://www.gov.uk/guidance/river-thames-restrictions-and-closures'

    # import into pandas
    pd_dfs = pd.read_html(url)

    # read with beautiful soup
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # find all tables
    tbls = soup.find_all('table')
    len(tbls)

    # function to find all links in a table
    def extract_links(table):
        links = []
        for tr in table.findAll("tr"):
            tds = tr.findAll("td")
            for td in tds:
                try:
                    link = td.find('a')['href']
                    links.append(link)
                except:
                    # links.append('')
                    pass
        return links

    def identify_river_closure_tables(x):
        correct = []
        for i in range(len(x)):
            nms = x[i].columns.values.tolist()
            if  nms == ['When', 'Where', 'What’s happening']:
                correct.append(i)
        return correct

    correct = identify_river_closure_tables(pd_dfs)
    pd_dfs = [pd_dfs[i] for i in correct]
    tbls = [tbls[i] for i in correct]

    # insert column of links into pandas dataframe
    for i in range(len(tbls)):
        new_link = extract_links(tbls[i])
        if len(new_link) == 0:
            new_link = ''
        pd_dfs[i]['link'] = new_link

    # concatenate all dataframes into one
    df = pd.concat(pd_dfs)

    # insert hyperlink

    links = []
    for i, el in enumerate(df['link']):
        event = df['What’s happening'].values[i]
        colon = str.find(event, ':')
        beg = event[:colon]
        end = event[colon:]
        # link = df['link'].values[i]
        link = el
        if link != '':
            links.append(f"<a href='{link}' target='_blank'>{beg}</a>{end}")
        else:
            links.append(f"{beg} {end}")
    
    df['Event'] = links
    df['Local'] = find_local(df['Where'].values)
    
    return df[['When', 'Where', 'Local', 'Event']]



def scrape_conditions():
    """
    Scrape conditions from environment agency and gov.uk websites
    """
    import re
    # url = 'http://riverconditions.environment-agency.gov.uk/'
    url = 'https://www.gov.uk/guidance/river-thames-current-river-conditions'

    try:
        dfs = pd.read_html(url)
        success = True
    except:
        success = False

    if success:
        dfs = dfs[0:3]
        df = pd.concat(dfs)
        # return(df)

        reach = df['Reach'].values

        # use a regular expression to extract the reach name
        fm = []
        to = []
        for r in reach:
            match = re.search('^(.*?) to (.*)$', r)
            if match:
                fm.append(match.group(1))
                to.append(match.group(2))
            else:
                fm.append(r)
                to.append('')

        df['From'] = fm
        df['To'] = to
        df['Local'] = find_local(df['From'].values)
        # print(df['Local'])
        return df[['From', 'To', 'Current conditions', 'Local']].reset_index(drop=True)
    else:
        return pd.DataFrame({"Result": ["No data available"]})


def sunrise_times():
    here = astral.Observer()

    s = sun(here, tzinfo = pytz.timezone("Europe/London"))

    events = pd.DataFrame({
        'event' : ['dawn', 'sunrise', 'sunset', 'dusk'],
        'time': [s['dawn'], s['sunrise'], s['sunset'], s['dusk']],
    })

    events['time'] = [strftime("%H:%M", t.timetuple()) for t in events['time']]
    return events
