import os
import time
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


def getAllReviews(reviews):
    allreviews = list()
    if len(reviews) == 0:
        return []
    for review in reviews:
        allreviews.append(cleanReview(review))
    return allreviews


def dictToPandas(review_list, animename, url, rank):
    columns = ['Review Date', 'Episodes Watched', 'Username', 'Review Likes',
               'Overall Rating', 'Story Rating', 'Animation Rating', 'Sound Rating',
               'Character Rating', 'Enjoyment Rating', 'Review']
    alldata = list()
    for curr in review_list:
        data = []
        for y in columns:
            data.append(curr.get(y, ''))
        alldata.append(data)
    df = pd.DataFrame(alldata, columns=columns)
    df['Anime Title'] = animename
    df['Anime URL'] = url
    df['Anime Rank'] = rank
    return df


def getAnimeReview(animename, url, rank):
    url = url[:-1] + "4"
    soup = BeautifulSoup(requests.get(url, timeout=10).text)
    reviews = soup.findAll('div', {"class": "borderDark"})
    review_list = cleanAllReviews(reviews)
    if len(review_list) == 0:
        time.sleep(30)
        soup = BeautifulSoup(requests.get(url, timeout=10).text)
        reviews = soup.findAll('div', {"class": "borderDark"})
        review_list = cleanAllReviews(reviews)
    df = dictToPandas(review_list, animename, url, rank)
    df.to_csv(f'Reviews/Review {rank}_3.csv', index=False)

# df = pd.read_csv('Top 200 Anime MAL.csv')[:10]
# for row in df.itertuples():
#    if row[0]>3400:
#        getAnimeReview(row[2], row[3], row[1])