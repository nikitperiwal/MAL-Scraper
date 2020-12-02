import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

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
        print("Link: ", animelink)
        print("Exception: ", e, "\n")
        return None
    soup = BeautifulSoup(webpage.text, features="html.parser")
    sidepanel = soup.find("td", {"class": "borderClass"}).find('div').findAll('div')[6:]
    data = cleanSidePanel(sidepanel)
    data['Summary'] = soup.find("p", {"class": ""}).text
    return data


def cleanDataFrame(df):
    """
    Cleans the DataFrame passed, to make the values more readable.

    Parameter:
        df: the dataframe to clean
    Returns:
        df: the cleaned dataframe
    """
    # Function to remove extra spaces from the cell inbetween items
    def cleanDivide(cell):
        cell = cell.split(',')
        for i in range(len(cell)):
            cell[i] = cell[i].strip()
        if cell[0] == "None found":
            return ''
        return ", ".join(cell)

    # Function to remove double entries from the cell.
    def removeDouble(cell):
        cell = cell.split(', ')
        for i in range(len(cell)):
            cell[i] = cell[i][:len(cell[i]) // 2]
        return ", ".join(cell)

    # Cleaning up the dataframe
    df['Genres'] = df['Genres'].apply(cleanDivide)
    df['Genres'] = df['Genres'].apply(removeDouble)
    df['Studios'] = df['Studios'].apply(cleanDivide)
    df['Producers'] = df['Producers'].apply(cleanDivide)
    df['Licensors'] = df['Licensors'].apply(cleanDivide)
    df['Score'] = df['Score'].apply(lambda x: x[:4])
    df['Ranked'] = df['Ranked'].apply(lambda x: x[1:-99])
    df['Members'] = df['Members'].str.replace(',', '')
    df['Favorites'] = df['Favorites'].str.replace(',', '')
    df['Popularity'] = df['Popularity'].str.replace('#', '')

    return df


def dictToPandas(data_dict_list):
    """
    Converts the passed list of dicts into a pandas DataFrame
    and returns the cleaned DataFrame

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
    dataframe = pd.DataFrame(alldata, columns=columns)
    return cleanDataFrame(dataframe)


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
