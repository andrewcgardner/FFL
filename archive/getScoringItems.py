import os
from pathlib import Path
import pandas as pd
import json

season = 2018
scoring_items = []

"""
for season in seasons:
    targetFile = "C:\\workspace\\python\\projects\\ffl\\new\\fullData\\leagueSettings" + str(season) + ".txt"
    with open(targetFile, 'r') as tF:
        data = json.load(tF)
"""
targetFile = "C:\\workspace\\python\\projects\\ffl\\new\\fullData\\leagueSettings" + str(season) + ".txt"
with open(targetFile, 'r') as tF:
    data = json.load(tF)

for d in data['leaguesettings']['scoringItems']:
    if d['statId'] not in scoring_items:
        scoring_items.append(d['statId'])

print(scoring_items)
