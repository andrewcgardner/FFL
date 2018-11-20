import os
from pathlib import Path
import pandas as pd
import numpy as np
import json
from pandas.io.json import json_normalize

def parseBox(json):
    df = json_normalize(json)
    
    # Columns we don't need, including stat totals (to be derived through aggregation)
    cols_to_drop = [
        'currentPeriodProjectedStats.appliedStatTotal'
        ,'currentPeriodRealStats.appliedStatTotal'
        ,'isQueuedWaiverLocked'
        ,'isTradeLocked'
        ,'lockStatus'
        ,'player.draftRank'
        ,'player.droppable'
        ,'player.eligibleSlotCategoryIds'
        ,'player.gameStarterStatus'
        ,'player.healthStatus'
        ,'player.isActive'
        ,'player.isIREligible'
        ,'player.jersey'
        ,'player.lastNewsDate'
        ,'player.lastVideoDate'
        ,'player.percentChange'
        ,'player.playerRatingSeason'
        ,'player.sportsId'
        ,'player.tickerId'
        ,'player.totalPoints'
        ,'player.universeId'
        ,'player.value'
        ,'watchList'
    ]
    for col in df.columns:
        if 'rawStats' in col:
            cols_to_drop.append(col)

    df = df.drop(cols_to_drop,axis=1)

    # Meta-data columns that we care about #
    id_cols = [
        'opponentProTeamId'
        ,'player.firstName'
        ,'player.lastName'
        ,'player.defaultPositionId'
        ,'player.percentOwned'
        ,'player.percentStarted'
        ,'player.playerId'
        ,'player.positionRank'
        ,'player.proTeamId'
        ,'proGameIds'
        ,'pvoRank'
        ,'slotCategoryId'
    ]

    value_cols = [
        col for col in df.columns if 'RealStats' in col
            or 'ProjectedStats' in col
    ]
    
    newdf = pd.melt(df, id_vars=id_cols, value_vars=value_cols, value_name='score')

    newdf['application'], newdf['unitType'], newdf['statTypeId'] = newdf['variable'].str.split('.').str
    newdf = newdf.drop('variable',axis=1)
    newdf = newdf[newdf['opponentProTeamId'] != -1] # exclude empty slots (potential for other fields to be used)
    newdf = newdf.replace('currentPeriod','',regex=True).replace('Stats','',regex=True)
    newdf['proGameIds'] = newdf['proGameIds'].str[0] #.astype(int)
    newdf = newdf.dropna(axis=0,subset=['score'])
    for val in ['Projected','Real']:
        newdf[val] = newdf.apply(lambda row: unmelt(row,val), axis=1)
    newdf = newdf.drop(['score','application','unitType'],axis=1)

    newdf = newdf.groupby(
        [col for col in newdf.columns if col != 'Projected' and col != 'Real']
            )[['Projected','Real']].sum()

    newdf['Real'].fillna(0,inplace=True)

    return newdf

def unmelt(row,targetVal):
    if row['application'] == targetVal:
        return row['score']
    else:
        return np.nan


def boxscores(data):
    full_box = pd.DataFrame()
    # Can this be altered to accept Home/Away parameter
        # This would allow for a single dataFrame to be returned,
        # which could be assigned to the HomeTeam or AwayTeam class object
    for n in range(0,len(data['boxscore']['teams'])):
        team = data['boxscore']['teams'][n]

        df = parseBox(team['slots'])
        
        # ADD DATAPOINTS:
        matchup = data['boxscore']['scheduleItems'][0]['matchups'][0]

        df['teamId'] = team['teamId']
        if team['teamId'] == matchup['awayTeamId']:
            df['opponentTeamId'] = matchup['homeTeamId']
        else:
            df['opponentTeamId'] = matchup['awayTeamId']
        df['homeTeamId'] = matchup['homeTeamId']
        df['awayTeamId'] = matchup['awayTeamId']

        df['seasonId'] = data['metadata']['seasonId']
        df['scoringPeriodId'] = data['boxscore']['scoringPeriodId']
        df['matchupTypeId'] = matchup['matchupTypeId']
        df['isBye'] = matchup['isBye']
             
        # OUTPUT: 
        #df.to_csv("C:\\workspace\\python\\projects\\ffl\\test_data\\2018-W2-T" + str(data['boxscore']['teams'][n]['teamId']) + ".csv")
        full_box = full_box.append(df)
    
    return full_box
    #full_box.to_csv("C:\\workspace\\python\\projects\\ffl\\test_data\\full_box.csv")
        

#teams = list(range(1,13))
teams = 4 # setting static value for initial testing

#weeks = list(range(1,6))
weeks = 2 # setting static value for initial testing

#targetFile = "C:\\workspace\\python\\projects\\ffl\\new\\fullData\\box\\2018-W1-T1.txt"
targetFile = 'C:\\workspace\\python\\projects\\ffl\\new\\fullData\\box\\2018-W' + str(weeks) + '-T' + str(teams) + '.txt'

with open(targetFile, 'r') as tF:
    data = json.load(tF)

boxscores(data)


#for item in data['boxscore']['teams']:
    #df = parseBox(item['slots'])
    #df.to_csv("C:\\workspace\\python\\projects\\ffl\\test_data\\2018-W2-T" + str(item['teamId']) + ".csv")
#    print(item)




"""" CURRENT STATE
for item in data['boxscore']['teams']:
    df = getBox(item['slots'])
    df.to_csv("C:\\workspace\\python\\projects\\ffl\\test_data\\2018-W2-T" + str(item['teamId']) + ".csv")
"""
# DATAPOINTS #
"""
scoringPeriodId = data['boxscore']['scoringPeriodId']
seasonId = data['metadata']['seasonId']

# HOME AND AWAY TEAMS
homeTeamId = data['boxscore']['scheduleItems'][0]['matchups'][0]['homeTeamId']
awayTeamId = data['boxscore']['scheduleItems'][0]['matchups'][0]['awayTeamId']
isBye = data['boxscore']['scheduleItems'][0]['matchups'][0]['isBye']

# HOME vs AWAY
if teams == homeTeamId:
    homeAwayId = 'Home'
    opponentTeamId = awayTeamId
else:
    homeAwayId = 'Away'
    opponentTeamId = homeTeamId
"""
"""
# BOXSCORE FOR DESIRED TEAM
for item in data['boxscore']['teams']:
    if item['teamId'] == teams:
        #print(item) # remove after testing
        #pass
        df = getBox(item['slots'])
        df.to_csv("C:\\workspace\\python\\projects\\ffl\\test_data\\2018-W2-T4.csv")
    else:
        pass
"""

