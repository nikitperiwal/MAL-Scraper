import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

def cleanRecs(recs):
    """
    Cleans the html source containing the recommendations and
    returns a dictionary containing the recommendations.

    Parameter:
        recs: html-recommendations extracted using bs4
    Returns:
        cleaned_recs: list of extracted recommendations
    """

    cleaned_recs = list()
    for rec in recs:
        name = rec.find('div', {'style': 'margin-bottom: 2px;'}).text.replace('\n', '').strip()[:-13]
        try:
            num = int(rec.find('div', {'class': 'spaceit'}).text[24:-10]) + 1
        except AttributeError:
            num = 1
        cleaned_recs.append([name, num])
    return cleaned_recs


def getRecs(recs_url):
    """
    Scrapes the user recommendation webpage for all recommendations and
    returns the cleaned recommendations in a list.

    Parameter:
        recs_url: link of the page to scrape recommendations from
    Returns:
        recs: list of all recommendations data
    """

    try:
        webpage = requests.get(recs_url, timeout=10)
    except requests.exceptions.RequestException as e:
        print("Link: ", recs_url)
        print("Exception: ", e, "\n")
        return None
    soup = BeautifulSoup(webpage.text, features="html.parser")

    recs = []
    for x in soup.findAll('div', {'class': 'borderClass'}):
        if len(x.findAll('div', {'class': 'borderClass'})) > 0:
            recs.append(x)
    recs = cleanRecs(recs)
    return recs


def recstoDataFrame(recs_list, anime_title, anime_url):
    """
    Converts the passed recs_list into a pandas DataFrame.

    Parameter:
        recs_list: list of anime recommendations
        anime_title: the title of the anime
        anime_url: the url of the anime
    Returns:
        dataframe: pandas DataFrame containing all recommendations
    """

    columns = ['Anime Title', 'Anime URL', 'Recommended Title', 'No. of Recommendations']
    dataframe = pd.DataFrame(recs_list, columns=columns[2:])
    dataframe['Anime Title'] = anime_title
    dataframe['Anime URL'] = anime_url
    dataframe = dataframe[columns]
    return dataframe


def getAnimeRecs(anime_title, anime_url, save_csv=True, csv_dir='Data/Recommendation/'):
    """
    Get Recommendations from an Anime whose details is passed,
    Stores the recommendations in a pandas DataFrame and returns it.
    Also, saves the dataFrame as a csv file if save_csv=True.

    Parameter:
        anime_title: the title of the anime
        anime_url: the url of the anime
        save_csv: Boolean, save the csv or not.
        csv_dir: directory to store the csv file in.
    Returns:
        reviews_df: pandas DataFrame containing recommendations for the anime
    """

    anime_url = anime_url + "/userrecs"
    recs = getRecs(anime_url)
    recs_df = recstoDataFrame(recs, anime_title, anime_url)

    if save_csv:
        if not os.path.exists(csv_dir):
            os.mkdir(csv_dir)
        anime_title = re.sub(r'[^a-zA-Z0-9]', '', anime_title)
        csv_filename = f'Anime Recommendations - {anime_title}.csv'
        fullname = os.path.join(csv_dir, csv_filename)
        recs_df.to_csv(fullname, index=False)

    return recs_df


def getAllAnimeRecommendations(anime_df, save_csv=True, save_individual=False, csv_dir='Data/'):
    """
    Get Recommendations for all Anime in the dataFrame passed,
    Stores all recommendations in a pandas DataFrame and returns it.
    Also, saves the dataFrame as a csv file if save_csv=True.

    Parameter:
        anime_df: dataFrame containing all anime details
        save_csv: Boolean, save the csv or not.
        save_individual: Boolean, save the individual anime recommendations as csv or not.
        csv_dir: directory to store the csv file in.
    Returns:
        anime_dataframe: pandas DataFrame containing recommendations for all anime
    """

    iterdata = zip(list(anime_df['Anime Title']), list(anime_df['MAL Link']))
    anime_dataframe = None
    for title, url in iterdata:
        if anime_dataframe is None:
            anime_dataframe = getAnimeRecs(title, url, save_csv=save_individual)
        else:
            anime_dataframe = anime_dataframe.append(getAnimeRecs(title, url, save_csv=save_individual))

    if save_csv:
        if not os.path.exists(csv_dir):
            os.mkdir(csv_dir)
        csv_filename = f'MAL Anime Recommendations.csv'
        fullname = os.path.join(csv_dir, csv_filename)
        anime_dataframe.to_csv(fullname, index=False)

    return anime_dataframe
