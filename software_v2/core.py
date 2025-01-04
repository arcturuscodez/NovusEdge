from options import o
from security import credentials
from psycopg2 import OperationalError

from database.connection import DatabaseConnection
from database.repositories.shareholder import ShareholderRepository
from database.models import ShareholderModel

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
                    from database.services.other.print_data import handle_print_table
                    handle_print_table(db_conn)
                elif o.AddShareholder:
                    from database.services.add.add_shareholder import handle_add_shareholder
                    handle_add_shareholder(db_conn)
                elif o.RemoveShareholder:
                    self.handle_remove_shareholder(db_conn)
                elif o.EditShareholder:
                    self.handle_edit_shareholder(db_conn)

        except OperationalError as e:
            print(f'An error occurred: {e}')
        except Exception as e:
            print(f'An unexpected error occurred: {e}')

    def handle_remove_shareholder(self, db_conn):
        try:
            shareholder_id = int(o.RemoveShareholder)
        except ValueError:
            print("RemoveShareholder requires a numeric ID.")
            return
        
        repository = ShareholderRepository(db_conn)
        success = repository.delete_shareholder(shareholder_id)
        if success:
            print(f"Successfully removed Shareholder with ID: {shareholder_id}")
        else:
            print(f"Failed to remove Shareholder with ID: {shareholder_id}")
    
    def handle_edit_shareholder(self, db_conn):
        parts = o.EditShareholder.split(':')
        if len(parts) != 5:
            print("Invalid format for EditShareholder. Expected format: id:name:ownership:investment:email")
            return
        try:
            shareholder_id = int(parts[0])
            name = parts[1]
            ownership = float(parts[2])
            investment = float(parts[3])
            email = parts[4]
        except ValueError:
            print("ID must be integer and Ownership & Investment must be numeric.")
            return
        
        repository = ShareholderRepository(db_conn)
        update_success = repository.update_shareholder(
            shareholder_id,
            name=name,
            ownership=ownership,
            investment=investment,
            email=email
        )
        if update_success:
            print(f"Successfully updated Shareholder with ID: {shareholder_id}")
        else:
            print(f"Failed to update Shareholder with ID: {shareholder_id}")

if __name__ == '__main__':
    NovusEdge()