from database import Database, Portfolio
from security import credentials


class Simulations:
    
    def __init__(self):
        """Set up the class for simulating portfolio performance."""
        self.db = credentials.DB
        self.user = credentials.USER
        self.password = credentials.PASSWORD
        self.host = credentials.HOST
        self.port = credentials.PORT
        self.pg_exe = credentials.PG_EXE_PATH
        
        tickers = self.connection()
        print(tickers)
        
    def collect_portfolio_data(self):
        with Database(db=self.db, user=self.user, password=self.password, host=self.host, port=self.port, pg_exe=self.pg_exe) as db:
            portfolio_data = db.fetch_data('PORTFOLIO')    
            
        

        return tickers
    
Simulations()

