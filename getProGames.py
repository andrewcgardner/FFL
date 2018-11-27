import pandas as pd
import json
from datetime import datetime
import numpy as np

#seasons = [2017,2018]
#weeks = [1,2]
#for seasonId in seasons:
#    for weekId in weeks:
#        targetFile = "C:\\workspace\\python\\projects\\ffl\\new\\fullData\\proGames" + str(seasonId) + "-" + str(weekId) + ".txt"
#        with open(targetFile, 'r') as tF:
#            data = json.load(tF)

seasonId = 2018
weekId = 1
targetFile = "C:\\workspace\\python\\projects\\ffl\\new\\fullData\\proGames" + str(seasonId) + "-" + str(weekId) + ".txt"
with open(targetFile, 'r') as tF:
    data = json.load(tF)

games = pd.DataFrame.from_dict(data['progames']['games'])

games['date'], games['time'] = games['gameDate'].str.split('T').str
games['time'] = games['time'].str.split('.').str[0]
games['gameDate'] = pd.to_datetime(games['date'] + ' ' + games['time'])
games.drop(['date','time','status'],axis=1,inplace=True)

print(games)
