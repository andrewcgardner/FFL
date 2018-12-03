import pandas as pd
import requests
import json
import getStats
from sqlalchemy import create_engine

class League(object):
    def __init__(self,leagueId,seasonId):
        self.leagueId = leagueId
        self.seasonId = seasonId
    
    def basicAPI(self,endpoint): # Can be removed after .txt testing #
    # .txt files to test at work
        targetFile = "C:\\workspace\\python\\projects\\ESPN\\FFL\\leagueData\\" + endpoint + str(self.seasonId) + ".txt"
        with open(targetFile, 'r') as tF:
            return json.load(tF)
     
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
                    int(self.seasonId)
                    ,teams['teams'][index]['division']['divisionId']
                    ,teams['teams'][index]['division']['divisionName']
                    ,int(teams['teams'][index]['teamId'])
                    ,teams['teams'][index]['teamAbbrev']
                    ,teams['teams'][index]['teamLocation'] + ' ' + teams['teams'][index]['teamNickname']
                    ,d['ownerId']
                    ,d['firstName'] + ' ' + d['lastName']
                    ,d['primaryOwner']
                ]
                
                teamList.append(ownerList)

        df = pd.DataFrame(teamList, columns = ['seasonId','divisionId','divisionName'
                                            ,'teamId','teamAbbrev','teamName'
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
        games.rename(columns={'gameId': 'proGameIds'},inplace=True)

        return games
    # The two class methods below can be removed after .txt testing
    def proGamesAPI(self):
        targetFile = "C:\\workspace\\python\\projects\\ESPN\\FFL\\leagueData\\proGames" \
            + str(self.seasonId) \
            + "-W" + str(self.scoringPeriodId) \
            + ".txt"
        with open(targetFile, 'r') as tF:
            return json.load(tF)

    def boxscoreAPI(self,homeTeamId):
        targetFile = "C:\\workspace\\python\\projects\\ESPN\\FFL\\boxscores\\" \
            + str(self.seasonId) \
            + "-W" + str(self.scoringPeriodId) \
            + "-T" + str(homeTeamId) \
            + ".txt"
        with open(targetFile, 'r') as tF:
            return json.load(tF)      

class Model(object):
    def __init__(self,leagueId,seasonId):
        self.leagueId = leagueId
        self.seasonId = seasonId

        pgsql = create_engine('postgresql://postgres:granite@localhost:5432/espn')

        L = League(self.leagueId,self.seasonId)
        
    ## Uncomment when using .txt files ##
        settings = L.basicAPI('leagueSettings')
        schedule = L.basicAPI('leagueSchedules')
        teams = L.basicAPI('teams')
    ## Uncomment when hitting the API directly ##
        #settings = L.extendAPI('leagueSettings')
        #schedule = L.extendAPI('leagueSchedules')
        #teams = L.extendAPI('teams')

        S = Season(L)
        weeks = S.weeksComplete(schedule)
        managers = S.getManagers(teams)
        weeks = [1,2]
        for week_num in weeks:
            W = Week(S,week_num)
            matchups = W.getMatchups(schedule)
            
            progames_json = W.proGamesAPI() # for .txt file testing
            #progames_json = L.extendAPI(endpoint='proGames',scoringPeriodId=week_num)
            progames = W.parseProGames(progames_json)

            for match in matchups:
                box_json = W.boxscoreAPI(match[0]) # for .txt file testing
                #box_json = L.extendAPI(endpoint='boxscore',scoringPeriodId=week_num,teamId=match[0])
                box_data = getStats.fullBox(box_json).reset_index()
                
            # Scoring Period information
                box_data['lastRegularWeek'] = settings['leaguesettings']['finalRegularSeasonMatchupPeriodId']
                box_data['lastPlayoffWeek'] = settings['leaguesettings']['finalScoringPeriodId']

            # Joining Manager table for additional metadata:
                box_data = pd.merge(left=box_data
                                    ,right=managers
                                            ,how='left'
                                            ,on=['teamId','seasonId'])
            # Joining Manager table for opponent metadata:
                box_data = pd.merge(left=box_data
                                    ,right=managers
                                            ,left_on=['opponentTeamId','seasonId']
                                            ,right_on=['teamId','seasonId']
                                            ,suffixes=['','.opponent'])
            # Joining Progames table for additional metadata:
                box_data = pd.merge(left=box_data
                                    ,right=progames
                                        ,how='left'
                                        ,on='proGameIds')
            # Publish data to PostgreSQL server
                box_data.to_sql('etl_api_boxscore_data',pgsql,schema='fantasyfootball',if_exists='append',index=False)
            # Publish data to .csv for testing
                #box_data.to_csv("C:\\workspace\\python\\projects\\ESPN\\FFL\\box_data.csv")

if __name__=='__main__':
    #league = input("Enter ESPN Fantasy Football League ID: ")
    #year = input("Enter desired season: ")
    #Model(league,year)
    Model(180704,2018)