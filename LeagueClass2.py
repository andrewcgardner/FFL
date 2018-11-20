import pandas as pd
import requests
import json
import getStats

class League(object):
    def __init__(self,leagueId,seasonId):
        self.leagueId = leagueId
        self.seasonId = seasonId
    
    def basicAPI(self,endpoint):
    # .txt files to test at work
        targetFile = "C:\\workspace\\python\\projects\\ESPN\\FFL\\leagueData\\" + endpoint + str(self.seasonId) + ".txt"
        with open(targetFile, 'r') as tF:
            return json.load(tF)
    
    # API Call for finalized process
    """    
        url = "http://games.espn.com/ffl/api/v2/" + endpoint
        params = {
            'leagueId': self.leagueId
            ,'seasonId': self.seasonId
        }
        
        return requests.get(url,params=params,cookies=None).json()
    """
 
class Season(object):
    def __init__(self,League):
        self.leagueId = League.leagueId
        self.seasonId = League.seasonId
    
    def weeksComplete(self,schedule):
        week_nums = []

        for item in schedule['leagueSchedule']['scheduleItems']:
            outcomes = 0
            for sub in item['matchups']:
                outcomes += sub['outcome']
            if outcomes > 0:
                week_nums.append(item['matchupPeriodId'])
       
        return week_nums
    
    def getManagers(self,teams):
        teamIndex = list(range(0,len(teams['teams'])))
        teamList = []
        for index in teamIndex:
            for d in teams['teams'][index]['owners']:
                ownerList = [
                    self.seasonId
                    ,teams['teams'][index]['teamId']
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
                    
    def describe(self):
        print(self.leagueId)
        print(self.seasonId)
    
    
class Week(object):
    def __init__(self,Season,scoringPeriodId):
        self.leagueId = Season.leagueId
        self.seasonId = Season.seasonId
        self.scoringPeriodId = scoringPeriodId
        #self.matchups = []
      

    def describe(self):
        print('LeagueID: ' + str(self.leagueId))
        print('Season: ' + str(self.seasonId))
        print('Week: ' + str(self.scoringPeriodId))

class Matchup(object):
    def __init__(self,Week):
        self.leagueId = Week.leagueId
        self.seasonId = Week.seasonId
        self.scoringPeriodId = Week.scoringPeriodId

    def boxscoreAPI(self,homeTeamId):
        targetFile = "C:\\workspace\\python\\projects\\ESPN\\FFL\\boxscores\\" \
            + str(self.seasonId) \
            + "-W" + str(self.scoringPeriodId) \
            + "-T" + str(homeTeamId) \
            + ".txt"
        with open(targetFile, 'r') as tF:
            return json.load(tF)
    # API Call for finalized process
    """   
        url = "http://games.espn.com/ffl/api/v2/boxscore"
        params = {
            'leagueId': self.leagueId
            ,'seasonId': self.seasonId
            ,'scoringPeriodId': self.scoringPeriodId
            ,'teamId': homeTeamId
        }
    
        return requests.get(url,params=params,cookies=None).json()
    """

class Model(object):
    def __init__(self,leagueId,seasonId):
        self.leagueId = leagueId
        self.seasonId = seasonId

        L = League(self.leagueId,self.seasonId)
        settings = L.basicAPI('leagueSettings')
        schedule = L.basicAPI('leagueSchedules')
        teams = L.basicAPI('teams')

        S = Season(L)
        weeks = S.weeksComplete(schedule)
        managers = S.getManagers(teams)



        W = Week(S,1)
        
        print(managers)


if __name__=='__main__':
    #league = input("Enter ESPN Fantasy Football League ID: ")
    #year = input("Enter desired season: ")
    #Model(league,year)
    Model(180704,2018)