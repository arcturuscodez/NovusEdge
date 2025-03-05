"""The main entry point for the NovusEdge application."""
from database.connection import DatabaseConnection, DatabaseServer
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

load_dotenv()

DBNAME = os.getenv('DB_NAME')
DBUSER = os.getenv('DB_USER')
DBPASS = os.getenv('DB_PASS')
DBHOST = os.getenv('DB_HOST')
DBPORT = os.getenv('DB_PORT')
PG_EXE = os.getenv('PG_EXE')

class NovusEdge:
    """Main class to handle NovusEdge functionality."""

    def __init__(self):
        """Initialize the application.""" 
        self.start_time = timer()

        self.server = DatabaseServer(DBHOST, DBPORT, PG_EXE)

    def _handle_server(self):
        """Handle server commands."""
        try:
            if args.action == 'start':
                self.server.start()
            elif args.action == 'stop':
                self._skip_daily_update = True
                try:
                    self.server.stop()
                except RuntimeError as e:
                    logger.warning(str(e))
                    return
            elif args.action == 'status':
                status = self.server.status()
                logger.info(f"PostgreSQL server status: {'Running' if status else 'Not running'}")
            elif args.action == 'restart':
                self._skip_daily_update = True
                try:
                    self.server.restart()
                except RuntimeError as e:
                    logger.warning(str(e))
                    return
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
        """
        Handle the read command to retrieve data from the database
        """
        from database.services.read import handle_print_table, handle_get_by_id
        if args.id:
            handle_get_by_id(self.db, args.table, args.id)
        else:
            handle_print_table(self.db, args.table)

    def _handle_update(self):
        """ 
        Handle the update command to update an entity in the database.
        """
        from database.services.update import handle_update_entity_by_id
        fields = dict(field.split('=') for field in args.fields)
        handle_update_entity_by_id(self.db, args.table, args.id, **fields)

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
        
        retriever.search_similar_tickers(query, limit)

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
            
            if args.command in ['search']:
                self._handle_search()
            elif args.command in ['server']:
                self._handle_server()
            else:
                with DatabaseConnection(
                    DBNAME, DBUSER, DBPASS, DBHOST, DBPORT
                ) as self.db:
                    if args.command == 'create':
                        self._handle_create()
                    elif args.command == 'read':
                        self._handle_read()
                    elif args.command == 'update':
                        self._handle_update()
                    elif args.command == 'delete':
                        self._handle_delete()

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