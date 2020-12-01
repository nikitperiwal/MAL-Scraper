def cleanSidePanel(sidepanel):
    data = dict()
    for x in sidepanel:
        x = x.text.strip().replace('\n','')
        index = x.find(':')
        if index==-1:
            continue
        y,x = x[:index], x[index+1:].strip()
        data[y] = x
    return data

def getAnimeDetail(animelink):
    try:
        soup = BeautifulSoup(requests.get(animelink, timeout=10).text)
        sidepanel = soup.find("td", {"class":"borderClass"}).find('div').findAll('div')[6:]
        data = cleanSidePanel(sidepanel)
        data['Summary'] = soup.find("p", {"class":""}).text
        return data
    except:
        return None

def getAllAnimeData(urllinks, titles):
    alldata = list()
    for url,name in zip(urllinks, titles):
        time.sleep(0.8)
        res = getAnimeDetail(url)
        if res==None:
            return alldata
        else:
            res['Anime Title'] = name
            res['MAL Url'] = url
            alldata.append(res)
    return alldata

def dictToPandas(all_data_dict):
    columns = ['Anime Title','MAL Url','English','Japanese','Type','Episodes',
               'Status','Aired','Premiered','Broadcast','Producers','Licensors',
               'Studios','Source','Genres','Duration','Rating','Score','Ranked',
               'Popularity','Members','Favorites','Summary']
    alldata = list()
    for curr in all_data_dict:
        data = []
        for y in columns:
            data.append(curr.get(y, ''))
        alldata.append(data)
    return pd.DataFrame(alldata, columns=columns)

df = pd.read_csv('Top 10000 Anime MAL.csv')
urllinks, titles = list(df['MAL Link']), list(df['Anime Title'])

i=9098
while i<10000:
    t = time.time()
    all_data_dict = getAllAnimeData(urllinks[i:i+500], titles[i:i+500])
    df = dictToPandas(all_data_dict)
    df.to_csv(f'MAL Anime List {i+1}-{i+len(df)}.csv', index=False)
    print(f'MAL Anime List {i+1}-{i+len(df)}.csv saved', (time.time()-t))
    i = i+len(df)
    time.sleep(60)