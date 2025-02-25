from database.connection import DatabaseConnection
from timeit import default_timer as timer
from options import args, parser

import os
import asyncio

from dotenv import load_dotenv

import logging

logger = logging.getLogger(__name__)

class NovusEdge:
    """Main class to handle the software's functionality."""
    
    logging_level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(
        level=logging_level,
        format='%(levelname)s:%(name)s:%(message)s'
    )
    
    load_dotenv()
    
    def __init__(self):
        """Set up the class for software usage."""
        
        self.db_params = {
            'db': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASS'),
            'host': os.getenv('DB_HOST'),
            'port': int(os.getenv('DB_PORT')),
            'pg_exe': os.getenv('PG_EXE')
        }
        
        self.start_time = timer()
            
        self.db = DatabaseConnection(**self.db_params)
        
        if self._is_db_option_set():
            self.database_usage()
        elif self._is_plot_option_set():
            pass
        else:
            print('No valid context for options was provided, please use -h to view valid options and uses.')

    def _is_db_option_set(self):
        """Check if any database-related option is set."""
        db_actions = []
        for group in parser._action_groups:
            if group.title == 'Database Options':
                db_actions.extend(group._group_actions)
        return any(getattr(args, action.dest) not in [None, False] for action in db_actions)
    
    def _is_plot_option_set(self):
        """Check if plotting option is set."""
        plot_option_dests = [
            'plotdata'
        ]
        return any(getattr(args, dest, False) not in [None, False] for dest in plot_option_dests)
    
    def database_usage(self):
        try:
            with self.db:
                from database.services.update import handle_daily_update, handle_update_portfolio_assets_data
                
                asyncio.run(handle_update_portfolio_assets_data(self.db))
                
                if args.StartServer:
                    self.db.start_server()
                elif args.PrintTable:
                    from database.services.other import handle_print_table
                    handle_print_table(self.db)
                elif args.AddShareholder:
                    from database.services.add import handle_add_shareholder
                    handle_add_shareholder(self.db)
                elif args.AddTransaction:
                    from database.services.add import handle_add_transaction
                    handle_add_transaction(self.db)
                elif args.AddFirm:
                    from database.services.add import handle_add_firm
                    handle_add_firm(self.db)
                elif args.AddExpense:
                    from database.services.add import handle_add_expense
                    handle_add_expense(self.db)
                elif args.AddRevenue:
                    from database.services.add import handle_add_revenue
                    handle_add_revenue(self.db)
                elif args.AddLiability:
                    from database.services.add import handle_add_liability
                    handle_add_liability(self.db)
                elif args.UpdateShareholder:
                    from database.services.update import handle_update_shareholder
                    handle_update_shareholder(self.db)
                elif args.UpdateTransaction:
                    from database.services.update import handle_update_transaction
                    handle_update_transaction(self.db)
                elif args.remove:
                    from database.services.delete import handle_delete_by_id
                    handle_delete_by_id(self.db)
                elif args.StopServer:
                    self.db.stop_server()
                elif args.table and not args.remove and not args.AddShareholder:
                    logger.error('No specific action provided for the table operation.')

                handle_daily_update(self.db)
            
        except AttributeError as e:
            logger.error(f'Argument parsing error: {e}')
                    
        except Exception as e:
            logger.error(f'An unexpected error occurred: {e}')
            raise
        
        finally:
            end_time = timer()
            elapsed = end_time - self.start_time
            logging.info(f'Elapsed time: {elapsed:.2f} seconds')
         
if __name__ == '__main__':
    NovusEdge()