from database.connection import DatabaseConnection
from dotenv import load_dotenv
from options import o

import os

import logging

logger = logging.getLogger(__name__)

class NovusEdge:
    """Main class to handle the software's functionality."""
    
    logging_level = logging.INFO if o.verbose else logging.WARNING
    logging.basicConfig(
        level=logging_level,
        format='%(levelname)s:%(name)s:%(message)s'
    )
    
    def __init__(self):
        """Set up the class for software usage."""
        
        load_dotenv()
        
        self.db = DatabaseConnection(
            db=os.getenv('DB'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            pg_exe=os.getenv('PG_EXE')
        )
        
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
            with self.db:
                if o.PrintTable:
                    from database.services.other import handle_print_table
                    handle_print_table(self.db)
                elif o.AddShareholder:
                    from database.services.add import handle_add_shareholder
                    handle_add_shareholder(self.db)
                    
        except Exception as e:
            raise
         
if __name__ == '__main__':
    NovusEdge()