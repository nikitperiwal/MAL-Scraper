import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor


def cleanSidePanel(sidepanel):
    """
    Cleans the SidePanel data and stores it in a dict.

    Parameter:
        sidepanel: html-sidepanel extracted using bs4
    Returns:
        data: dict of extracted data
    """

    data = dict()
    for x in sidepanel:
        x = x.text.strip().replace('\n', '')
        index = x.find(':')
        if index == -1:
            continue
        y, x = x[:index], x[index+1:].strip()
        data[y] = x
    return data


def getAnimeDetail(animelink):
    """
    Cleans the SidePanel data and stores it in a dict.

    Parameter:
        sidepanel: html-sidepanel extracted using bs4
    Returns:
        data: dict of extracted data
    """

    try:
        webpage = requests.get(animelink, timeout=10)
    except requests.exceptions.RequestException as e:
        print(e)
        return None
    soup = BeautifulSoup(webpage.text, features="html.parser")
    sidepanel = soup.find("td", {"class": "borderClass"}).find('div').findAll('div')[6:]
    data = cleanSidePanel(sidepanel)
    data['Summary'] = soup.find("p", {"class": ""}).text
    return data


def dictToPandas(data_dict_list):
    """
    Converts the passed list of dicts into a pandas DataFrame.

    Parameter:
        data_dict_list: list containing scraped data dicts.
    Returns:
        the dataframe containing the scraped data as a table
    """

    columns = ['Anime Title', 'MAL Url', 'English', 'Japanese', 'Type', 'Episodes',
               'Status', 'Aired', 'Premiered', 'Broadcast', 'Producers', 'Licensors',
               'Studios', 'Source', 'Genres', 'Duration', 'Rating', 'Score', 'Ranked',
               'Popularity', 'Members', 'Favorites', 'Summary']
    alldata = list()

    for curr in data_dict_list:
        data = []
        for y in columns:
            data.append(curr.get(y, ''))
        alldata.append(data)
    return pd.DataFrame(alldata, columns=columns)


def getAllAnimeData(anime_df, save_csv=True, csv_dir='Data/', sleep_time=1):
    """
    Scrapes details of all anime in the DataFrame passed and
    returns the scraped details as a pandas DataFrame.
    Also, saves a csv file if 'save_csv' set to True.

    Parameter:
        anime_df: dataframe containing anime title, url
        save_csv: Boolean, save the csv or not
        csv_dir: the directory to save the csv file in
        sleep_time: the time to sleep between each page request.
    Returns:
        data: dict of extracted data
    """

    alldata = list()
    iterdata = zip(list(anime_df['MAL Link']), list(anime_df['Anime Title']))
    for url, name in iterdata:
        # Delays the program so that the website do not stop responding.
        time.sleep(sleep_time)
        res = getAnimeDetail(url)
        if res is None:
            return alldata
        else:
            res['Anime Title'] = name
            res['MAL Url'] = url
            alldata.append(res)

    dataframe = dictToPandas(alldata)

    # Saves the csv.
    if save_csv:
        csv_filename = f'{len(anime_df)} Anime Details MAL.csv'
        if not os.path.exists(csv_dir):
            os.mkdir(csv_dir)
        fullname = os.path.join(csv_dir, csv_filename)
        dataframe.to_csv(fullname, index=False)

    return dataframe

