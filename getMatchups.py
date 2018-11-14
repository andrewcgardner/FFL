import os
from pathlib import Path
import pandas as pd
import json
from pandas.io.json import json_normalize

targetFile = "C:\workspace\python\projects\\ffl\json\\schedule.txt"
with open(targetFile, 'r') as tF:
    data = json.load(tF)

#matchup_count = list(range(0,6)) # 6 can be replaced by number of teams in league, divided by two
"""
ids = []
for matchup in matchup_count:
    homeTeam = data['leagueSchedule']['scheduleItems'][1]['matchups'][matchup]['homeTeam']
    awayTeam = data['leagueSchedule']['scheduleItems'][1]['matchups'][matchup]['awayTeam']
    # print(homeTeam['teamAbbrev'] + ' vs. ' + awayTeam['teamAbbrev'])
    ids.append([homeTeam['teamId'],awayTeam['teamId']])
print(ids)
"""

weeks = list(range(0,data['leagueSchedule']['regularSeasonMatchupPeriodCount'])) # replaced hardcoded 13 
for week in weeks:
    if data['leagueSchedule']['scheduleItems'][week]['matchups'][0]['outcome'] == 0:
        latest_week = week
        break

# FULL SCHEDULE OF MATCHUPS #
full_season = {}
for week in range(0,latest_week):
    ids = []
    for matchup in data['leagueSchedule']['scheduleItems'][week]['matchups']:
        homeTeam = matchup['homeTeam']
        awayTeam = matchup['awayTeam']
        # print(homeTeam['teamAbbrev'] + ' vs. ' + awayTeam['teamAbbrev'])
        ids.append([homeTeam['teamId'],awayTeam['teamId']])
    #print(ids)
    full_season[week + 1] = ids

print(full_season)




"""
weeks = list(range(0,13))

for week in weeks:
    print('Week ' + str(data['leagueSchedule']['scheduleItems'][week]['matchupPeriodId']) + ': '
        + str(data['leagueSchedule']['scheduleItems'][week]['matchups'][0]['outcome'])
        )
# LATEST WEEK #        
for week in weeks:
    if data['leagueSchedule']['scheduleItems'][week]['matchups'][0]['outcome'] == 0:
        print(data['leagueSchedule']['scheduleItems'][week]['matchupPeriodId'])
        break
# LIST OF COMPLETED WEEKS #        
completed = []
for week in weeks:
    if data['leagueSchedule']['scheduleItems'][week]['matchups'][0]['outcome'] > 0:
        completed.append(data['leagueSchedule']['scheduleItems'][week]['matchupPeriodId'])
print(completed)
"""
