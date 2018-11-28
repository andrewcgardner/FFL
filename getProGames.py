import pandas as pd
from datetime import datetime

def parseProGames(json):
    games = pd.DataFrame.from_dict(json['progames']['games'])
    games['date'], games['time'] = games['gameDate'].str.split('T').str
    games['time'] = games['time'].str.split('.').str[0]
    games['gameDate'] = pd.to_datetime(games['date'] + ' ' + games['time'])
    games.drop(['date','time','status'],axis=1,inplace=True)

    return games