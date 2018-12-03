from sqlalchemy import create_engine

def ConnectPostgreSQL(user,password,database,server='localhost',port=5342):
    return create_engine("postgresql://" 
                            + user + ":" 
                            + str(password) + "@"
                            + str(server) + ":"
                            + str(port) + "/"
                            + str(database)
                        )