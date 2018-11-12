import os
from pathlib import Path
import pandas as pd
import json
from pandas.io.json import json_normalize

seasons = [2017,2018]
teamList = []

for season in seasons:
    targetFile = "C:\\workspace\\python\\projects\\ffl\\new\\fullData\\teams" + str(season) + ".txt"
    with open(targetFile, 'r') as tF:
        data = json.load(tF)

    teamIndex = list(range(0,len(data['teams'])))
    
    for index in teamIndex:
        for d in data['teams'][index]['owners']:
            ownerList = [
                season
                ,data['teams'][index]['teamId']
                ,d['firstName']
                ,d['lastName']
                ,d['firstName'] + ' ' + d['lastName']
                ,d['primaryOwner']
            ]
            
            teamList.append(ownerList)

df = pd.DataFrame(teamList, columns=['season','teamId','firstName','lastName','fullName','isPrimary'])

primary = df[df['isPrimary']]
secondary = df[df['isPrimary'] == False]
outputcols = ['season','teamId','firstName','lastName','fullName']

final = pd.merge(
    primary[outputcols]
    ,secondary[outputcols]
    ,how='left'
    ,on=['season','teamId']
    ,suffixes=('','.secondary')
    )

print(final)