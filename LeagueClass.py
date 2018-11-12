class League(object):
    def __init__ (self,leagueId,cookies=None):
        self.leagueId = leagueId

class Season(League):
    def __init__ (self,seasonId):
        self.seasonId = seasonId
        self.league = League(123456)
        self.leagueId = self.league.leagueId

    def testing_testing_testing(self):
        print(self.leagueId)

if __name__ == '__main__':
    a = Season(123)
    a.testing_testing_testing()

