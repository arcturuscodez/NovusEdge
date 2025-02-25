"""Service module for handling the deletion of an entity from a table."""
from options import args
from psycopg2.errors import UndefinedTable
from database.repositories.factory import RepositoryNotFoundError
from database.repositories.base import GenericRepository

import logging

logger = logging.getLogger(__name__)

def handle_delete_by_id(db) -> bool: 
    """
    Handle the deletion of an entity from a table by ID.

    Args:
        db (object): The database connection object.
        
    Returns:
        bool: True if the entity was deleted successfully, False otherwise.

    """
    try:
        if not args.table:
            logger.error('Table name not provided.')
            print('Error: Table name is required for deletion')
            return
        
        repository = GenericRepository(db, args.table)
        result = repository.delete(args.remove)
        if result:
            logger.info(f'Entity with id: {args.remove} from table: {args.table} deleted sucessfully.')
            print(f'Entity with id: {args.remove} from table: {args.table} deleted sucessfully.')
            return result
        else:
            print('Failed to delete entity.')
            return False
        
    except RepositoryNotFoundError as e:
        logger.error(f'Repository not found error: {e}')
    except UndefinedTable as e:
        logger.error(f'Table not found, deletion failed: {e}')
    except Exception as e:
        logger.error(f'An error occurred handling the deletion of an entity from the table: {e}')
        raise
        