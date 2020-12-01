import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor


def cleanTableData(table):
    """
    Cleans the table data and stores it in a list of data.

    Parameter:
        table: html-table extracted using bs4
    Returns:
        alldata: list of all data extracted
    """

    alldata = list()
    for row in table.findAll("tr")[1:]:
        data = []
        celllist = (row.findAll('td')[:3])

        # Extracting Ranking
        data.append(celllist[0].text.replace('\n', ''))

        # Extracting Name, Link
        namelink = celllist[1].findAll('a')[1]
        data.append(namelink.text)
        data.append(namelink['href'])

        # Extracting Episodes, Airing, Members
        info = celllist[1].find('div', {'class': 'information di-ib mt4'}).text.split('\n')
        for x in info:
            x = x.strip()
            if len(x) != 0:
                data.append(x)

        # Extracting MAL Score
        data.append(celllist[2].text.replace('\n', ''))

        alldata.append(data)
    return alldata


def getListData(animelistlink):
    """
    Extracts the data from the top-anime webpage,
    and returns it as a list of data after cleaning.

    Parameter:
        animelistlink: the link of the webpage
    """

    try:
        webpage = requests.get(animelistlink, timeout=10)
    except requests.exceptions.RequestException as e:
        print(e)
        return []
    soup = BeautifulSoup(webpage.text, features='html.parser')
    table = soup.find("table", {"class": "top-ranking-table"})
    return cleanTableData(table)


def getTopData(anime_toplist_link, topnum=200):
    """
    Scrapes list of all top 'topnum' anime from the passed link 'anime_toplist_link'
    and returns the extracted data.
    Uses ThreadPool to speed up the process of scraping.

    Parameters:
        anime_toplist_link: the link of the top-anime list
        topnum: the number of animes to scrape detail of
    Returns:
        alldata: scraped list of data of all anime
    """

    # Using Threading to speed up the scraping process
    # and collecting all threads in a list.
    futurelist = list()
    with ThreadPoolExecutor(max_workers=20) as executor:
        for i in range(0, topnum, 50):
            list_link = anime_toplist_link + str(i)
            futurelist.append(executor.submit(getListData, list_link))

    # Collecting all the returned values from the threads.
    alldata = list()
    for x in futurelist:
        alldata.extend(x.result())

    return alldata


def getTopAnimeDataFrame(num=200, save_csv=True, csv_dir='Data/'):
    """
    Scrapes list of all top 'num' anime from the passed link 'anime_toplist_link'
    and returns the extracted data as a pandas DataFrame.
    Also, saves a csv file if 'save_csv' set to True.

    Parameters:
        num: the number of animes to scrape detail of
        save_csv: Boolean, save the csv or not
        csv_dir: the directory to save the csv file in
    Returns:
        dataframe: the dataframe containing the scraped data as a table
    """

    anime_toplist_link = "https://myanimelist.net/topanime.php?limit="
    animedata = getTopData(anime_toplist_link, num)

    # Creates the pandas DataFrame
    columns = ['Ranking', 'Anime Title', 'MAL Link', 'Airing Type and Episode',
               'Airing Time', 'No. of Members', 'MAL Score']
    dataframe = pd.DataFrame(animedata, columns=columns)

    # Saves the csv.
    if save_csv:
        csv_filename = f'Top {num} Anime MAL.csv'
        if not os.path.exists(csv_dir):
            os.mkdir(csv_dir)
        fullname = os.path.join(csv_dir, csv_filename)
        dataframe.to_csv(fullname, index=False)

    return dataframe
