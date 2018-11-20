import os
from pathlib import Path
import pandas as pd
import json
"""
seasons = [2017,2018]
teamList = []

for seasonId in seasons:
    targetFile = "C:\\workspace\\python\\projects\\ffl\\new\\fullData\\teams" + str(seasonId) + ".txt"
    with open(targetFile, 'r') as tF:
        data = json.load(tF)

    teamIndex = list(range(0,len(data['teams'])))
    
    for index in teamIndex:
        for d in data['teams'][index]['owners']:
            ownerList = [
                seasonId
                ,data['teams'][index]['division']['divisionId']
                ,data['teams'][index]['division']['divisionName']
                ,data['teams'][index]['teamId']
                ,data['teams'][index]['teamAbbrev']
                ,data['teams'][index]['teamLocation']
                ,data['teams'][index]['teamNickname']
                ,d['ownerId']
                ,d['firstName'] + ' ' + d['lastName']
                ,d['primaryOwner']
            ]
            
            teamList.append(ownerList)

df = pd.DataFrame(teamList, columns = ['seasonId','divisionId','divisionName'
                                        ,'teamId','teamAbbrev','teamLocation','teamNickname'
                                        ,'ownerId','fullName','isPrimary'])

primary = df[df['isPrimary']]
secondary = df[df['isPrimary'] == False]
output_pri = [col for col in primary if col != 'isPrimary']
output_sec = ['seasonId','teamId','ownerId','fullName']

final = pd.merge(
    primary[output_pri]
    ,secondary[output_sec]
    ,how='left'
    ,on=['seasonId','teamId']
    ,suffixes=('','.secondary')
    )

print(final)
"""

def getManagers(teams,seasonId):
        teamIndex = list(range(0,len(teams['teams'])))
        teamList = []
        for index in teamIndex:
            for d in teams['teams'][index]['owners']:
                ownerList = [
                    seasonId
                    ,teams['teams'][index]['division']['divisionId']
                    ,teams['teams'][index]['division']['divisionName']
                    ,teams['teams'][index]['teamId']
                    ,teams['teams'][index]['teamAbbrev']
                    ,teams['teams'][index]['teamLocation']
                    ,teams['teams'][index]['teamNickname']
                    ,d['ownerId']
                    ,d['firstName'] + ' ' + d['lastName']
                    ,d['primaryOwner']
                ]
                
                teamList.append(ownerList)

        df = pd.DataFrame(teamList, columns = ['seasonId','divisionId','divisionName'
                                        ,'teamId','teamAbbrev','teamLocation','teamNickname'
                                        ,'ownerId','fullName','isPrimary'])

        primary = df[df['isPrimary']]
        secondary = df[df['isPrimary'] == False]
        output_pri = [col for col in primary if col != 'isPrimary']
        output_sec = ['seasonId','teamId','ownerId','fullName']

        final = pd.merge(
            primary[output_pri]
            ,secondary[output_sec]
            ,how='left'
            ,on=['seasonId','teamId']
            ,suffixes=('','.secondary')
            )
        return final

seasons = [2017,2018]   
for seasonId in seasons:
    targetFile = "C:\\workspace\\python\\projects\\ffl\\new\\fullData\\teams" + str(seasonId) + ".txt"
    with open(targetFile, 'r') as tF:
        data = json.load(tF)
        print(getManagers(data,seasonId))