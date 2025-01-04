from database import queries
from options import o
from security import credentials
from psycopg2 import OperationalError

from software_v2.database import connection

class NovusEdge:

    def __init__(self):
        """Set up the class for software usage."""
        self.db = credentials.DB
        self.user = credentials.USER
        self.password = credentials.PASSWORD
        self.host = credentials.HOST
        self.port = credentials.PORT
        self.pg_exe = credentials.PG_EXE_PATH
        
    def _is_db_option_set(self):
        pass
    
    def _is_plot_option_set(self):
        pass
    
    def database_usage(self):
        try:
            pass
        except OperationalError as e:
            print(f'An error occurred: {e}')
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
    
    def plotting_usage(self):
        try:
            pass
        except OperationalError as e:
            print(f'An error occurred: {e}')
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
            
if __name__ == '__main__':
    NovusEdge()