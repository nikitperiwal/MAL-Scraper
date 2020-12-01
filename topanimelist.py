import requests
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor


def getListData(animelistlink):
    """
    Extracts the data from the top-anime webpage,
    and returns it in the form of an array of data.
    Parameter:
        animelistlink: the link of the webpage
    """
    webpage = requests.get(animelistlink)
    soup = BeautifulSoup(webpage.text)
    table = soup.find("table", {"class": "top-ranking-table"})

    alldata = list()
    for row in table.findAll("tr")[1:]:
        data = []
        celllist = (row.findAll('td')[:3])
        # Ranking
        data.append(celllist[0].text.replace('\n', ''))
        # Name, Link, Episodes, Airing, Members
        namelink = celllist[1].findAll('a')[1]
        data.append(namelink.text)
        data.append(namelink['href'])
        info = celllist[1].find('div', {'class': 'information di-ib mt4'}).text.split('\n')
        for x in info:
            x = x.strip()
            if len(x) != 0:
                data.append(x)
        # MAL Score
        data.append(celllist[2].text.replace('\n', ''))
        alldata.append(data)
    return alldata


def getAllAnimeData(topnum=200):
    topanimelink = "https://myanimelist.net/topanime.php?limit="
    futurelist = list()
    with ThreadPoolExecutor(max_workers=20) as executor:
        for i in range(0, topnum, 50):
            list_link = topanimelink + str(i)
            futurelist.append(executor.submit(getListData, list_link))
    alldata = list()
    for x in futurelist:
        alldata.extend(x.result())
    return alldata


num = 10000
animedata = getAllAnimeData(num)
columns = ['Ranking', 'Anime Title', 'MAL Link', 'Airing Type and Episode', 'Airing Time', 'No. of Members',
           'MAL Score']
df = pd.DataFrame(animedata, columns=columns)
df.to_csv(f'Top {num} Anime MAL.csv', index=False)
len(df)