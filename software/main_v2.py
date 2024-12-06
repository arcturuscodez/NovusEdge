from database_v2 import Database, Shareholder, Firm
from sql import queries_v2 as q
from options import o
from security import credentials
from stocks import StocksManager
from psycopg2 import OperationalError

class NovusEdge:
    
    def __init__(self):
        """Set up the class for software usage."""
        self.db = credentials.DB
        self.user = credentials.USER
        self.password = credentials.PASSWORD
        self.host = credentials.HOST
        self.port = credentials.PORT
        self.pg_exe = credentials.PG_EXE_PATH
        
        self.run()
        
    def run(self):
        try:
            with Database(db=self.db, user=self.user, password=self.password, host=self.host, port=self.port, pg_exe=self.pg_exe) as db:
                
                sm = Shareholder(db.connection, db.cursor)
                fm = Firm(db.connection, db.cursor)
                
                if o.PrintTable:
                    db.fetch_data(str(o.PrintTable).upper(), print_data=True)
                elif o.AddShareholder:
                    parts = o.AddShareholder.split(':')
                    sm.shareholder_add(name=parts[0], ownership=int(parts[1]), investment=float(parts[2]), email=parts[3])
                    
                fm.update_total_investments()
                fm.update_firm_total_value()
        
        except OperationalError as e:
            print(f'Failed to connect to the database: {e}')
        except Exception as e:
            print(f'An unexepected error occured: {e}')

if __name__ == '__main__':
    NovusEdge()