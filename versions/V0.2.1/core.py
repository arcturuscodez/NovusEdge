from database.connection import DatabaseConnection
from dotenv import load_dotenv
from options import args

import os

import logging

logger = logging.getLogger(__name__)

dotenv_path = os.path.abspath('config/.env')
if os.path.exists(dotenv_path):
    load_dotenv(verbose=True, dotenv_path=dotenv_path)
    logger.info(f'.env file loaded from {dotenv_path}')
else:
    logger.error(f'.env file not found at {dotenv_path}')

class NovusEdge:
    """Main class to handle the software's functionality."""
    
    logging_level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(
        level=logging_level,
        format='%(levelname)s:%(name)s:%(message)s'
    )
    
    def __init__(self):
        """Set up the class for software usage."""
        
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
            'Remove'
        ]
        return any(getattr(args, dest) not in [None, False] for dest in db_option_dests)
    
    def _is_plot_option_set(self):
        """Check if plotting option is set."""
        plot_option_dests = [
            'plotdata'
        ]
        return any(getattr(args, dest) not in [None, False] for dest in plot_option_dests)
    
    def database_usage(self):
        try:
            with self.db:
                if args.PrintTable:
                    from database.services.other import handle_print_table
                    handle_print_table(self.db)
                elif args.AddShareholder:
                    from database.services.add import handle_add_shareholder
                    handle_add_shareholder(self.db)
                elif args.Remove:
                    from database.services.delete import handle_delete_by_id
                    handle_delete_by_id(self.db)
                    
        except Exception as e:
            raise
         
if __name__ == '__main__':
    NovusEdge()