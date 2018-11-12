import os
from pathlib import Path
import pandas as pd
import json
from pandas.io.json import json_normalize

def getBox(json):
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
    newdf = newdf[newdf['opponentProTeamId'] != -1]
    #newdf = newdf[newdf['unitType'] == 'applied']
    newdf = newdf.replace('currentPeriod','',regex=True).replace('Stats','',regex=True)
    newdf['proGameIds'] = newdf['proGameIds'].str[0] #.astype(int)

    #newdf = newdf.pivot_table(index=[c for c in newdf.columns if c != 'application'], columns='application',values='score', aggfunc=', '.join)

    # STILL NEED TO:
        # - Unpivot real/projected stats
        # - Exclude NaN stats
        # - Exclude ineligible scoring items
    #
    #print(newdf)
    return newdf


teams = list(range(1,13))
teams = 4 # setting static value for initial testing

weeks = list(range(1,6))
weeks = 2 # setting static value for initial testing

targetFile = "C:\\workspace\\python\\projects\\ffl\\new\\fullData\\box\\2018-W1-T1.txt"
targetFile = 'C:\\workspace\\python\\projects\\ffl\\new\\fullData\\box\\2018-W' + str(weeks) + '-T' + str(teams) + '.txt'

with open(targetFile, 'r') as tF:
    data = json.load(tF)

#for d in data['boxscore']:
#    print(d)


# DATAPOINTS #

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

# BOXSCORE FOR DESIRED TEAM
for item in data['boxscore']['teams']:
    if item['teamId'] == teams:
        #print(item) # remove after testing
        #pass
        df = getBox(item['slots'])
        df.to_csv("C:\\workspace\\python\\projects\\ffl\\new\\2018-W2-T4.csv")
    else:
        pass