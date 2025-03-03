"""The main entry point for the NovusEdge application."""
from database.connection import DatabaseConnection
from timeit import default_timer as timer
from options import args
from dotenv import load_dotenv
import os
import asyncio
import logging

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG if args.debug else logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)        

class NovusEdge:
    """Main class to handle NovusEdge functionality."""

    def __init__(self):
        """Initialize the application.""" 
        
        load_dotenv() # Load environment variables from .env file
        
        self.db_params = {
            'db': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASS'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'pg_exe': os.getenv('PG_EXE')
        }
        self.start_time = timer()
        
        self.db = DatabaseConnection(**self.db_params) # Initialize database connection

    def _handle_server(self):
        """Handle server commands."""
        try:
            if args.action == 'start':
                self.db.start_server()
            elif args.action == 'stop':
                self._skip_daily_update = True
                self.db.stop_server()
            elif args.action == 'check':
                self.db._check_server_status()
            else:
                logger.error(f"Unsupported server action: {args.action}")
                return
            
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise

    # Command Handlers
    def _handle_create(self):
        """ 
        Handle the create command to add a new entity to the database.
        """
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
        self._execute_handler(handlers, args.type)

    def _handle_read(self):
        from database.services.read import handle_print_table
        handle_print_table(self.db, args.table)

    def _handle_update(self):
        """ 
        Handle the update command to update an entity in the database.
        """
        from database.services.update import handle_update_entity
        handlers = {
            'entity': handle_update_entity
        }
        self._execute_handler(handlers, args.type, with_id=True)

    def _handle_delete(self):
        """ 
        Handle the delete command to remove an entity from the database.
        """
        from database.services.delete import handle_delete_by_id
        handle_delete_by_id(self.db, args.table, args.id)

    def _daily_update(self):
        """ 
        Handle the daily update command to update the database with new data.
        """
        from database.services.update import handle_daily_update, handle_update_portfolio_assets_data
        asyncio.run(handle_update_portfolio_assets_data(self.db))
        handle_daily_update(self.db, force_update=args.override)
    
    def _handle_search(self):
        """
        Handle the search command to find tickers.
        """
        from icarus.retriever import AssetRetriever
        
        query = args.query
        limit = args.limit
        
        retriever = AssetRetriever("TEMP")
        
        results = retriever.search_similar_tickers(query, limit)
        
        if results:
            
            symbol_width = max(10, max(len(r['symbol']) for r in results))
            name_width = max(20, max(len(r['name']) for r in results))
            exchange_width = max(10, max(len(r['exchange']) for r in results))
            type_width = max(8, max(len(r['type']) for r in results))

            print("\nSearch Results:")
            print(f"{'Symbol':<{symbol_width}} {'Name':<{name_width}} {'Exchange':<{exchange_width}} {'Type':<{type_width}}")
            print("-" * (symbol_width + name_width + exchange_width + type_width + 6))
            
            for result in results:
                print(f"{result['symbol']:<{symbol_width}} {result['name']:<{name_width}} {result['exchange']:<{exchange_width}} {result['type']:<{type_width}}")

            print(f"\nFound {len(results)} results for '{query}'")
        else:
            print(f"No results found for '{query}'")

    def _filter_global_args(self, args_dict):
        """
        Filter out global arguments from args dictionary.
        
        Args:
            args_dict: Dictionary of command line arguments
            
        Returns:
            filtered_args: Dictionary of arguments without global args
        """
        filtered_args = args_dict.copy()
        global_args = ['command', 'type', 'debug', 'override']
        for arg in global_args:
            filtered_args.pop(arg, None)
        return filtered_args
    
    def _execute_handler(self, handlers_dict, entity_type, with_id=False):
        """
        Execute the appropriate handler function for an entity type.

        Args:
            handlers_dict: Dictionary mapping entity types to handler functions
            entity_type: Type of entity to handle
            with_id: Whether handler requires an ID parameter

        Returns:
            success: Whether handler executed successfully
        """
        handler = handlers_dict.get(entity_type)
        if not handler:
            logger.error(f"Unsupported entity type: {entity_type}")
            return False

        entity_args = self._filter_global_args(vars(args))

        try:
            if with_id:
                entity_id = entity_args.pop('id', None)
                handler(self.db, entity_id, **entity_args)
            else:
                handler(self.db, **entity_args)
            return True
        except Exception as e:
            logger.error(f"Error handling {entity_type}: {e}")
            return False
        
    def run(self):
        """
        Execute the command specified by the user.
        """
        try:
            with self.db:
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
                elif args.command == 'search':
                    self._handle_search()

                if args.command not in ['server', 'search']:
                    self._daily_update()
        except Exception as e:
            if not hasattr(self, '_skip_daily_update'):
                logger.error(f"An unexpected error occurred: {e}")
            raise
        
        finally:
            elapsed = timer() - self.start_time
            if not hasattr(self, '_skip_daily_update'):
                logger.info(f"Elapsed time: {elapsed:.2f} seconds")
    
if __name__ == "__main__":
    app = NovusEdge()
    app.run()