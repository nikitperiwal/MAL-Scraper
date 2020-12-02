import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

def cleanReview(review):
    """
    Cleans the html source containing the review and
    returns a dictionary containing the review elements.

    Parameter:
        review: html-review extracted using bs4
    Returns:
        review_items: dict of extracted review items
    """

    cleaned_review = list()
    for x in review.findAll(text=True):
        x = x.replace('\n', '').strip()
        if len(x) != 0 and x != "Preliminary":
            cleaned_review.append(x)

    # Inserts the cleaned review into a dict.
    review_items = dict()
    review_items['Review Date'] = cleaned_review[0]
    review_items['Episodes Watched'] = cleaned_review[1]
    review_items['Username'] = cleaned_review[4]
    review_items['Review Likes'] = cleaned_review[8]
    review_items['Overall Rating'] = cleaned_review[11]
    review_items['Story Rating'] = cleaned_review[13]
    review_items['Animation Rating'] = cleaned_review[15]
    review_items['Sound Rating'] = cleaned_review[17]
    review_items['Character Rating'] = cleaned_review[19]
    review_items['Enjoyment Rating'] = cleaned_review[21]
    review_items['Review'] = "\n".join(cleaned_review[22:-5])
    return review_items


def getAllReviews(review_link):
    """
    Scrapes the review webpage for all reviews and
    returns the cleaned reviews in a list.

    Parameter:
        review_link: link of the page to scrape reviews from
    Returns:
        allreviews: list of all reviews data
    """

    try:
        webpage = requests.get(review_link, timeout=10)
    except requests.exceptions.RequestException as e:
        print("Link: ", review_link)
        print("Exception: ", e, "\n")
        return None
    soup = BeautifulSoup(webpage.text, features="html.parser")
    reviews = soup.findAll('div', {"class": "borderDark"})

    # Collecting all reviews in a list, after cleaning.
    allreviews = list()
    for review in reviews:
        allreviews.append(cleanReview(review))
    return allreviews


def reviewstoDataframe(review_list, anime_title, anime_url):
    """
    Converts the passed review_list into a pandas DataFrame.

    Parameter:
        review_list: list of anime reviews
        anime_title: the title of the anime
        anime_url: the url of the anime
    Returns:
        dataframe: pandas DataFrame containing all reviews
    """

    columns = ['Review Date', 'Episodes Watched', 'Username', 'Review Likes',
               'Overall Rating', 'Story Rating', 'Animation Rating', 'Sound Rating',
               'Character Rating', 'Enjoyment Rating', 'Review']
    alldata = list()
    for curr in review_list:
        data = []
        for y in columns:
            data.append(curr.get(y, ''))
        alldata.append(data)

    # Creating dataFrame
    dataframe = pd.DataFrame(alldata, columns=columns)
    dataframe['Anime Title'] = anime_title
    dataframe['Anime URL'] = anime_url
    columns = ['Anime Title', 'Anime URL']+columns
    dataframe = dataframe[columns]
    return dataframe


def getAnimeReview(anime_title, anime_url, save_csv=True, csv_dir='Data/Reviews/'):
    """
    Get Reviews from an Anime whose details is passed,
    Stores the reviews in a pandas DataFrame and returns it.
    Also, saves the dataFrame as a csv file if save_csv=True.

    Parameter:
        anime_title: the title of the anime
        anime_url: the url of the anime
        save_csv: Boolean, save the csv or not.
        csv_dir: directory to store the csv file in.
    Returns:
        reviews_df: pandas DataFrame containing all reviews for the anime
    """

    anime_url = anime_url + "/reviews"
    reviews = getAllReviews(anime_url)
    reviews_df = reviewstoDataframe(reviews, anime_title, anime_url)

    if save_csv:
        if not os.path.exists(csv_dir):
            os.mkdir(csv_dir)
        anime_title = re.sub(r'[^a-zA-Z0-9]', '', anime_title)
        csv_filename = f'Anime Review - {anime_title}.csv'
        fullname = os.path.join(csv_dir, csv_filename)
        reviews_df.to_csv(fullname, index=False)
    return reviews_df


def getAllAnimeReviews(anime_df, save_csv=True, save_individual=False, csv_dir='Data/'):
    """
    Get Reviews from all Anime in the dataFrame passed,
    Stores all reviews in a pandas DataFrame and returns it.
    Also, saves the dataFrame as a csv file if save_csv=True.

    Parameter:
        anime_df: dataFrame containing all anime details
        save_csv: Boolean, save the csv or not.
        save_individual: Boolean, save the individual anime reviews as csv or not.
        csv_dir: directory to store the csv file in.
    Returns:
        anime_dataframe: pandas DataFrame containing reviews for all anime
    """

    iterdata = zip(list(anime_df['Anime Title']), list(anime_df['MAL Link']))
    anime_dataframe = None
    for title, url in iterdata:
        if anime_dataframe is None:
            anime_dataframe = getAnimeReview(title, url, save_csv=save_individual)
        else:
            anime_dataframe = anime_dataframe.append(getAnimeReview(title, url, save_csv=save_individual))

    if save_csv:
        if not os.path.exists(csv_dir):
            os.mkdir(csv_dir)
        csv_filename = f'MAL Anime Reviews.csv'
        fullname = os.path.join(csv_dir, csv_filename)
        anime_dataframe.to_csv(fullname, index=False)

    return anime_dataframe
