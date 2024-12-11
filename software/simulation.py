from database import Database
from security import credentials

class Simulations:
    
    def __init__(self):
        """Set up the class for simulating portfolio performance."""
        with Database(db=credentials.DB, user=credentials.USER, password=credentials.PASSWORD, host=credentials.HOST, port=credentials.PORT, pg_exe=credentials.PG_EXE_PATH) as self.db:
            data = self.db.fetch_data('PORTFOLIO')
            print(data)
    
Simulations()

