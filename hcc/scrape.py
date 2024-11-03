
import requests
from bs4 import BeautifulSoup
import pandas as pd
import hcc
from hcc.core import find_local

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
        # print(f"Table {i} has {len(new_link)} links")
        # print(f"Table {i} has {len(pd_dfs[i])} rows")
        if len(new_link) != len(pd_dfs[i]):
            pd_dfs[i]['link'] = [''] * len(pd_dfs[i])
        else:
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
    df['Local'] = hcc.core.find_local(df['Where'].values)
    
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
    except Exception as e:
        print(f"Error: {e}")
        success = False

    if success:
        # Correct column names
        for df in dfs:
            df.columns = ['Reach', 'Current conditions']
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
        df['Local'] = hcc.find_local(df['From'].values)
        # print(df['Local'])
        return df[['From', 'To', 'Current conditions', 'Local']].reset_index(drop=True)
    else:
        return pd.DataFrame({"Result": ["No data available"]})

