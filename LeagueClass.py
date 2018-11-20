import pandas as pd
import requests
import json
import getStats

class Matchup(object):
    def __init__(self,matchups):
        self.matchups = matchups
        #self.boxscore = getBoxscore(self.matchups)


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
    def __init__(self,leagueId,year):
        self.leagueId = leagueId
        self.year = year
        self.settings = self.basicAPI('leagueSettings')
        self.teams = self.basicAPI('teams')
        self.schedule = self.basicAPI('leagueSchedules')
        self.scoringperiods = self.getScoringPeriods()
        self.managers = self.getManagers()
        
        
    def basicAPI(self,endpoint):
        # .txt files to test at work
        targetFile = "C:\\workspace\\python\\projects\\ESPN\\FFL\\leagueData\\" + endpoint + str(self.year) + ".txt"
        with open(targetFile, 'r') as tF:
            return json.load(tF)
    
    # API Call for finalized process
    """    
        url = "http://games.espn.com/ffl/api/v2/" + endpoint
        params = {
            'leagueId': self.leagueId
            ,'seasonId': self.year
        }
        
        return requests.get(url,params=params,cookies=None).json()
    """
    def boxscoreAPI(self,scoringPeriodId,homeTeamId):
        targetFile = "C:\\workspace\\python\\projects\\ESPN\\FFL\\boxscores\\" \
            + str(self.year) \
            + "-W" + str(scoringPeriodId) \
            + "-T" + str(homeTeamId) \
            + ".txt"
        with open(targetFile, 'r') as tF:
            return json.load(tF)
    # API Call for finalized process
    """   
        url = "http://games.espn.com/ffl/api/v2/boxscore"
        params = {
            'leagueId': self.leagueId
            ,'seasonId': self.year
            ,'scoringPeriodId': scoringPeriodId
            ,'teamId': homeTeamId
        }
    
        return requests.get(url,params=params,cookies=None).json()
    """

    def getManagers(self):
        teamIndex = list(range(0,len(self.teams['teams'])))
        teamList = []
        for index in teamIndex:
            for d in self.teams['teams'][index]['owners']:
                ownerList = [
                    self.year
                    ,self.teams['teams'][index]['teamId']
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
        return final


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
        self.season = Season(self.leagueId,self.seasonId)
        
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
    

