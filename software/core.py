"The main entry point for the NovusEdge application."
from database.connection import DatabaseConnection
from timeit import default_timer as timer
from options import args
from dotenv import load_dotenv
import os
import asyncio
import logging

logger = logging.getLogger(__name__)

logging.basicConfig(
            level=logging.DEBUG if args.verbose else logging.INFO,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )           
        
logger = logging.getLogger(__name__)

class NovusEdge:
    """Main class to handle NovusEdge functionality."""

    def __init__(self):
        """Initialize the application."""
        
        load_dotenv()
        self.db_params = {
            'db': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASS'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'pg_exe': os.getenv('PG_EXE')
        }
        self.start_time = timer()
        self.db = DatabaseConnection(**self.db_params)

    def _handle_server(self):
        """Handle server commands."""
        try:
            if args.action == 'start':
                self.db.start_server()
            elif args.action == 'stop':
                self._skip_daily_update = True
                self.db.stop_server()
                return
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise
    
    def run(self):
        """Execute the command specified by the user."""
        try:
            with self.db:
                # Dispatch based on subcommand
                if args.command == 'create':
                    self._handle_create()
                elif args.command == 'server':
                    self._handle_server()
                elif args.command == 'read':
                    self._handle_read()
                elif args.command == 'update':
                    self._handle_update()
                elif args.command == 'delete':
                    self._handle_delete()

                if args.command != 'server':
                    self._daily_update() # Run daily update (if applicable due to TASK_METADATA check)

        except Exception as e:
            if not hasattr(self, '_skip_daily_update'):
                logger.error(f"An unexpected error occurred: {e}")
            raise
        finally:
            elapsed = timer() - self.start_time
            if not hasattr(self, '_skip_daily_update'):
                logger.info(f"Elapsed time: {elapsed:.2f} seconds")

    # Command Handlers
    def _handle_create(self):
        from database.services.create import (
            handle_create_shareholder, handle_create_transaction, handle_create_firm,
            handle_create_expense, handle_create_revenue, handle_create_liability
        )
        handlers = {
            'shareholder': handle_create_shareholder,
            'transaction': handle_create_transaction,
            'firm': handle_create_firm,
            'expense': handle_create_expense,
            'revenue': handle_create_revenue,
            'liability': handle_create_liability
        }
        if args.data:
            data = dict(kv.split('=') for kv in args.data.split(':'))
            handler = handlers.get(args.type)
            handler(self.db, **data) if handler else logger.error(f"Unsupported add type: {args.type}")
        else:
            logger.error("Data required for 'create' command")

    def _handle_read(self):
        from database.services.read import handle_print_table
        handle_print_table(self.db, args.table)

    def _handle_update(self):
        from database.services.update import handle_update_shareholder, handle_update_transaction
        handlers = {
            'shareholder': handle_update_shareholder,
            'transaction': handle_update_transaction
        }
        if args.data:
            data = dict(kv.split('=') for kv in args.data.split(':'))
            handler = handlers.get(args.type)
            handler(self.db, args.id, **data) if handler else logger.error(f"Unsupported update type: {args.type}")
        else:
            logger.error("Data required for 'update' command")

    def _handle_delete(self):
        from database.services.delete import handle_delete_by_id
        handle_delete_by_id(self.db, args.table, args.id)

    def _daily_update(self):
        from database.services.update import handle_daily_update, handle_update_portfolio_assets_data
        asyncio.run(handle_update_portfolio_assets_data(self.db))
        handle_daily_update(self.db, force_update=args.override)

if __name__ == "__main__":
    app = NovusEdge()
    app.run()