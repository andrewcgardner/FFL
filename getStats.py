import pandas as pd
import numpy as np
from pandas.io.json import json_normalize

def unmelt(row,targetVal):
    if row['application'] == targetVal:
        return row['score']
    else:
        return np.nan

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
        # Added the below columns to drop until I have a strategy to use them in analysis #
        ,'player.positionRank'
        ,'player.percentOwned'
        ,'player.percentStarted'
        ,'pvoRank'
    ]
    for col in df.columns:
        if 'rawStats' in col:
            cols_to_drop.append(col)

    df = df.drop(cols_to_drop,axis=1)

    # Meta-data columns that we care about #
    ## Commented out the most fluid of fields until I have a strategy to use them in analysis #
    id_cols = [
        'opponentProTeamId'
        ,'player.firstName'
        ,'player.lastName'
        ,'player.defaultPositionId'
        #,'player.percentOwned'
        #,'player.percentStarted'
        ,'player.playerId'
        #,'player.positionRank'
        ,'player.proTeamId'
        ,'proGameIds'
        #,'pvoRank'
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
    newdf['playerName'] = newdf['player.firstName'] + ' ' + newdf['player.lastName']
    newdf = newdf.drop(['score','application','unitType','player.firstName','player.lastName'],axis=1)

    newdf = newdf.groupby(
        [col for col in newdf.columns if col != 'Projected' and col != 'Real']
            )[['Projected','Real']].sum()

    newdf['Real'].fillna(0,inplace=True)
    newdf['Projected'].fillna(0,inplace=True)

    return newdf

def fullBox(data):
    full_box = pd.DataFrame()

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

        df['seasonId'] = int(data['metadata']['seasonId'])
        df['scoringPeriodId'] = data['boxscore']['scoringPeriodId']
        df['matchupTypeId'] = matchup['matchupTypeId']
        df['isBye'] = matchup['isBye']
             
        full_box = full_box.append(df)
    
    return full_box