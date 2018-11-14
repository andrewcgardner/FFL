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
    def __init__(self,schedule,scoringPeriodId):
        self.schedule = schedule
        self.scoringPeriodId = scoringPeriodId
        self.matchups = self.getMatchups()
        
    def getMatchups(self):
        pairings = []
        for matchup in self.schedule['leagueSchedule']['scheduleItems'][self.scoringPeriodId - 1]['matchups']:
            homeTeam = matchup['homeTeam']
            awayTeam = matchup['awayTeam']
            pairings.append([homeTeam['teamId'],awayTeam['teamId']])
        
        return pairings



class Season(object):
    def __init__(self,year):
        self.year = year
        self.settings = self.basicAPI('leagueSettings')     #self.getSettings_txt()
        self.teams = self.basicAPI('teams')                 #self.getTeams_txt()
        self.schedule = self.basicAPI('leagueSchedules')    #self.getSchedule_txt()
        self.scoringperiods = self.getScoringPeriods()
        
        
    def basicAPI(self,endpoint):
        # .txt files to test at work
        targetFile = "C:\\workspace\\python\\projects\\ESPN\\FFL\\leagueData\\" + endpoint + str(self.year) + ".txt"
        with open(targetFile, 'r') as tF:
            return json.load(tF)

    def getScoringPeriods(self):
        week_nums = []

        for item in self.schedule['leagueSchedule']['scheduleItems']:
            outcomes = 0
            for sub in item['matchups']:
                outcomes += sub['outcome']
            if outcomes > 0:
                week_nums.append(item['matchupPeriodId'])
       
        period_dict = {}
        for week in week_nums:
            period_dict[week] = ScoringPeriod(self.schedule,week)

        return period_dict
        
class League(object):
    def __init__ (self,leagueId,seasonId,cookies=None):
        self.leagueId = leagueId
        self.seasonId = seasonId
        self.season = Season(self.seasonId)
        
        """ ## logic to handle lists as well as ints ##
        if self.seasonId.__class__.__name__ == 'list':
            print('list')
        else:
            print(self.seasonId.__class__.__name__)
        """
        


if __name__ == '__main__':
    theFFL = League(123456,2018)
    twenty_eighteen = theFFL.season

    for sched in twenty_eighteen.scoringperiods:
        print(twenty_eighteen.scoringperiods[sched].scoringPeriodId, ': ', twenty_eighteen.scoringperiods[sched].matchups)
    

