def clean1(s):
    s = s.split(',')
    for i in range(len(s)):
        s[i] = s[i].strip()
    if s[0] == "None found":
        return ''
    return ", ".join(s)

def clean2(s):
    s = s.split(', ')
    for i in range(len(s)):
        s[i] = s[i][:len(s[i])//2]
    return ", ".join(s)

def cleanDF(df):
    df['Favorites'] = df['Favorites'].str.replace(',','')
    df['Members'] = df['Members'].str.replace(',','')
    df['Producers'] = df['Producers'].apply(clean1)
    df['Licensors'] = df['Licensors'].apply(clean1)
    df['Genres'] = df['Genres'].apply(clean1)
    df['Genres'] = df['Genres'].apply(clean2)
    df['Score'] = df['Score'].apply(lambda x: x[:4])
    df['Ranked'] = df['Ranked'].apply(lambda x: x[1:-99])
    df['Popularity'] = df['Popularity'].apply(lambda x: x[1:])
    return df