from database.connection import DatabaseConnection
from dotenv import load_dotenv
from options import o

import os

class NovusEdge:
    
    load_dotenv()
    
    DB = os.getenv('DB')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    PG_EXE = os.getenv('PG_EXE')
    
    def __init__(self):
        """Set up the class for software usage."""
        self.db = NovusEdge.DB
        self.user = NovusEdge.DB_USER
        self.password = NovusEdge.DB_PASSWORD
        self.host = NovusEdge.DB_HOST
        self.port = NovusEdge.DB_PORT
        self.pg_exe = NovusEdge.PG_EXE
        
        if self._is_db_option_set():
            self.database_usage()
        elif self._is_plot_option_set():
            pass
        else:
            print('An error occurred. No options were set.')
        
    def _is_db_option_set(self):
        """Check if any database-related option is set."""
        db_option_dests = [
            'PrintTable',
            'AddShareholder',
            'RemoveShareholder',
            'EditShareholder',
            'BuyStock',
            'SellStock',
            'AddTransaction',
            'Truncate',
            'InitializeFirmTable'
        ]
        return any(getattr(o, dest) not in [None, False] for dest in db_option_dests)
    
    def _is_plot_option_set(self):
        """Check if plotting option is set."""
        plot_option_dests = [
            'plotdata'
        ]
        return any(getattr(o, dest) not in [None, False] for dest in plot_option_dests)
    
    def database_usage(self):
        try:
            with DatabaseConnection(db=self.db, user=self.user, password=self.password, 
                                    host=self.host, port=self.port, pg_exe=self.pg_exe) as db_conn:
                if o.PrintTable:
                    from database.services.other import handle_print_table
                    handle_print_table(db_conn)
                    
        except Exception as e:
            raise
         
if __name__ == '__main__':
    NovusEdge()