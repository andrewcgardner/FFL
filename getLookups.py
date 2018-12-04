import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

pgsql = create_engine("postgresql://postgres:granite@localhost:5432/espn")

filepath = os.path.join(Path.cwd(), 'leagueData')

for f in os.listdir('leagueData'):
    csv = os.path.join(filepath,f)
    tablename = f.replace('.csv','')

    with open(csv,'r') as tF:
        df = pd.read_csv(tF)
        df.to_sql(tablename,pgsql,schema='fantasyfootball',if_exists='replace',index=False)
