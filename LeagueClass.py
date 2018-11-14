import pandas
import requests
import json

class HomeTeam(object):
    def __init__ (self):
        self.elements = {}

class AwayTeam(object):
    def __init__ (self):
        self.elements = {}

class Matchup(object):
    def __init__(self):
        self.teams = {}

class ScoringPeriod(object):
    def __init__(self):
        self.matchups = {}

class Season(object):
    def __init__(self,year):
        self.year = year
        self.settings = {}
        self.teams = {}
        self.schedule = {}
        self.scoringperiods = {}

    def getSettings_txt(self):
        # for testing at work, to include/adjust for API calls
        targetFile = "C:\\workspace\\python\\projects\\ESPN\\FFL\\leagueData\\leagueSettings" + str(self.year) + ".txt"
        with open(targetFile, 'r') as tF:
            self.settings = json.load(tF) # appends full settings file \\ narrow down to required jpaths
    
    def getTeams_txt(self):
        # for testing at work, to include/adjust for API calls
        targetFile = "C:\\workspace\\python\\projects\\ESPN\\FFL\\leagueData\\teams" + str(self.year) + ".txt"
        with open(targetFile, 'r') as tF:
            self.teams = json.load(tF)

    def getSchedule_txt(self):
        # for testing at work, to include/adjust for API calls
        targetFile = "C:\\workspace\\python\\projects\\ESPN\\FFL\\leagueData\\leagueSchedule" + str(self.year) + ".txt"
        with open(targetFile, 'r') as tF:
            self.schedule = json.load(tF)

class League(object):
    def __init__ (self,leagueId,seasonId,cookies=None):
        self.leagueId = leagueId
        self.seasonId = seasonId
        self.Season = Season(self.seasonId)
        """
        if self.seasonId.__class__.__name__ == 'list':
            print('list')
        else:
            print(self.seasonId.__class__.__name__)
        """
        
"""
    def seasonSettings_txt(self):
        # for testing at work, to include/adjust for API calls
        targetFile = "C:\\workspace\\python\\projects\\ESPN\\FFL\\leagueData\\leagueSettings" + str(self.seasonId) + ".txt"
        with open(targetFile, 'r') as tF:
            self.seasons[self.seasonId] = {}
            self.seasons[self.seasonId]['settings'] = json.load(tF) # appends full settings file \\ narrow down to required jpaths
"""


if __name__ == '__main__':
    a = League(123456,2018)
    a.Season.getSettings_txt()
    a.Season.getTeams_txt()
    print(a.Season.settings['leaguesettings']['name'])
    for s in a.Season.settings['leaguesettings']:
        print(s)
