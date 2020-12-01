def cleanRecs(recs):
    cleaned = list()
    for rec in recs:
        name = rec.find('div', {'style': 'margin-bottom: 2px;'}).text.replace('\n', '').strip()[:-13]
        try:
            num = int(rec.find('div', {'class': 'spaceit'}).text[24:-10]) + 1
        except:
            num = 1
        cleaned.append([name, num])
    return cleaned


def getAnimeRecs(rank, anime, url, count=1):
    soup = BeautifulSoup(requests.get(url, timeout=10).text)
    recs = []
    for x in soup.findAll('div', {'class': 'borderClass'}):
        if len(x.findAll('div', {'class': 'borderClass'})) > 0:
            recs.append(x)
    recs = cleanRecs(recs)
    columns = ['Rank', 'Anime Title', 'Anime URL', 'Recommended Title', 'No. of Recommendations']
    df = pd.DataFrame(recs, columns=columns[3:])
    df['Rank'] = rank
    df['Anime Title'] = anime
    df['Anime URL'] = url
    if len(df) != 0:
        df.to_csv(f'Recs/Recs_{rank}.csv', index=False)
    else:
        if count == 1:
            time.sleep(30)
            getAnimeRecs(rank, anime, url, count=2)
            print([rank, anime, url])


df = pd.read_csv('Top 10000 Anime MAL.csv')
for row in df.itertuples():
    if row[0] > 2239:
        getAnimeRecs(row[1], row[2], row[3] + "/userrecs")