import pandas as pd
import requests
import json
import getStats
#from utils import connections

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
        
    #    url = "http://games.espn.com/ffl/api/v2/" + endpoint
    #    params = {
    #        'leagueId': self.leagueId
    #        ,'seasonId': self.seasonId
    #    }
        
    #    return requests.get(url,params=params,cookies=None).json()
    # 
    def extendAPI(self,endpoint,**kwargs):
        url = "http://games.espn.com/ffl/api/v2/" + endpoint
        params = {
            'leagueId': self.leagueId
            ,'seasonId': self.seasonId
        }
        for key in ['scoringPeriodId','teamId']:
            if key in kwargs:
                params[key] = kwargs.get(key)
        
        return requests.get(url,params=params,cookies=None).json()
        
 
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
                    
    def describe(self):
        print(self.leagueId)
        print(self.seasonId)
    
    
class Week(object):
    def __init__(self,Season,scoringPeriodId):
        self.leagueId = Season.leagueId
        self.seasonId = Season.seasonId
        self.scoringPeriodId = scoringPeriodId
            
    def getMatchups(self,schedule):
        ids = []
        matchup_index = self.scoringPeriodId - 1
        for matchup in schedule['leagueSchedule']['scheduleItems'][matchup_index]['matchups']:
            homeTeam = matchup['homeTeam']
            awayTeam = matchup['awayTeam']
            ids.append([homeTeam['teamId'],awayTeam['teamId']])

        return ids

    def parseProGames(self,json):
        games = pd.DataFrame.from_dict(json['progames']['games'])
        games['date'], games['time'] = games['gameDate'].str.split('T').str
        games['time'] = games['time'].str.split('.').str[0]
        games['gameDate'] = pd.to_datetime(games['date'] + ' ' + games['time'])
        games.drop(['date','time','status'],axis=1,inplace=True)

        return games      

    def describe(self):
        print('LeagueID: ' + str(self.leagueId))
        print('Season: ' + str(self.seasonId))
        print('Week: ' + str(self.scoringPeriodId))

# CAN BE REMOVED WHEN .txt TESTING IS NO LONGER NECESSARY
class Matchup(object):
    def __init__(self,Week):
        self.leagueId = Week.leagueId
        self.seasonId = Week.seasonId
        self.scoringPeriodId = Week.scoringPeriodId

    def getBoxscore(self,homeTeamId):
        box_json = self.boxscoreAPI(homeTeamId)
        box = getStats.boxscores(box_json)
        return box

    def boxscoreAPI(self,homeTeamId):
        targetFile = "C:\\workspace\\python\\projects\\ESPN\\FFL\\boxscores\\" \
            + str(self.seasonId) \
            + "-W" + str(self.scoringPeriodId) \
            + "-T" + str(homeTeamId) \
            + ".txt"
        with open(targetFile, 'r') as tF:
            return json.load(tF)
    # API Call for finalized process
       
    #    url = "http://games.espn.com/ffl/api/v2/boxscore"
    #    params = {
    #        'leagueId': self.leagueId
    #        ,'seasonId': self.seasonId
    #        ,'scoringPeriodId': self.scoringPeriodId
    #        ,'teamId': homeTeamId
    #    }
    
    #    return requests.get(url,params=params,cookies=None).json()
    

class Model(object):
    def __init__(self,leagueId,seasonId):
        self.leagueId = leagueId
        self.seasonId = seasonId

        #ods = connections.SQLConnect()

        L = League(self.leagueId,self.seasonId)
        settings = L.extendAPI('leagueSettings')
        schedule = L.extendAPI('leagueSchedules')
        teams = L.extendAPI('teams')

        S = Season(L)
        weeks = S.weeksComplete(schedule)
        managers = S.getManagers(teams)

        #print(managers)
        #managers.to_sql('temp_acg_managers',ods,schema='SbPowerUser',if_exists='append')
        #box_json = self.extendAPI('boxscore',scoringPeriodId=self.scoringPeriodId,teamId=homeTeamId)
        for week_num in weeks:
            W = Week(S,week_num)
            matchups = W.getMatchups(schedule)
            progames_json = L.extendAPI(endpoint='proGames',scoringPeriodId=week_num)
            progames = W.parseProGames(progames_json)

            for match in matchups:
                box_json = L.extendAPI(endpoint='boxscore',scoringPeriodId=week_num,teamId=match[0])
                box_data = getStats.boxscores(box_json).reset_index()
                # Below to be used in .txt file testing
                #M = Matchup(W)
                #box_data = M.getBoxscore(match[0]).reset_index() # columns were getting lost in multi-index
                
                # Joining Manager table for additional metadata:
                box_data = pd.merge(left=box_data
                                    ,right=managers
                                            ,how='left'
                                            ,on=['teamId','seasonId'])
                box_data = pd.merge(left=box_data
                                    ,right=managers
                                            ,how='left'
                                            ,left_on=['opponentTeamId','seasonId']
                                            ,right_on=['teamId','seasonId']
                                            ,suffixes=('','.opponent'))
        print(box_data.head(5))
                #box_data.to_sql('temp_acg_boxscores',ods,schema='SbPowerUser',if_exists='append')


if __name__=='__main__':
    #league = input("Enter ESPN Fantasy Football League ID: ")
    #year = input("Enter desired season: ")
    #Model(league,year)
    Model(180704,2018)