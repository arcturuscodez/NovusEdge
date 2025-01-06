from options import o
from security import credentials
from psycopg2 import OperationalError

from database.connection import DatabaseConnection

class NovusEdge:

    def __init__(self):
        """Set up the class for software usage."""
        self.db = credentials.DB
        self.user = credentials.USER
        self.password = credentials.PASSWORD
        self.host = credentials.HOST
        self.port = credentials.PORT
        self.pg_exe = credentials.PG_EXE_PATH

        if self._is_db_option_set():
            self.database_usage()
        elif self._is_plot_option_set():
            self.plotting_usage()
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
            with DatabaseConnection(db=self.db, user=self.user, password=self.password, host=self.host, port=self.port, pg_exe=self.pg_exe) as db_conn:
                if o.PrintTable:
                    from database.services.other import handle_print_table
                    handle_print_table(db_conn)
                elif o.AddShareholder:
                    from database.services.add import handle_add_shareholder
                    handle_add_shareholder(db_conn)
                elif o.RemoveShareholder:
                    from database.services.remove import handle_remove_shareholder
                    handle_remove_shareholder(db_conn)
                elif o.EditShareholder:
                    from database.services.edit import handle_edit_shareholder
                    handle_edit_shareholder(db_conn)
                elif o.AddTransaction:
                    from database.services.add import handle_add_transaction
                    handle_add_transaction(db_conn)
                elif o.EditTransaction:
                    pass
                

        except OperationalError as e:
            print(f'An error occurred: {e}')
        except Exception as e:
            print(f'An unexpected error occurred: {e}')

if __name__ == '__main__':
    NovusEdge()