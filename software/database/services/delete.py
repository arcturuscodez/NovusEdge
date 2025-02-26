"""Service module for handling the deletion of an entity from a table."""
from psycopg2.errors import UndefinedTable
from database.repositories.factory import RepositoryNotFoundError
from database.repositories.base import GenericRepository
from database.connection import DatabaseConnection

import logging

logger = logging.getLogger(__name__)

def handle_delete_by_id(db: DatabaseConnection, table: str, entity_id: int) -> bool:
    """
    Handle the deletion of an entity from a table by ID.

    Args:
        db (DatabaseConnection): The database connection object.
        table (str): The name of the table to delete from.
        entity_id (int): The ID of the entity to delete.

    Returns:
        bool: True if the entity was deleted successfully, False otherwise.
    """
    try:
        if not table:
            logger.error("Table name not provided for deletion")
            return False

        if not isinstance(entity_id, int):
            logger.error(f"Entity ID must be an integer, got {type(entity_id)}")
            return False

        logger.debug(f"Attempting to delete entity ID {entity_id} from table '{table}'")
        repository = GenericRepository(db, table)
        result = repository.delete(entity_id)

        if result:
            logger.info(f"Entity with ID {entity_id} from table '{table}' deleted successfully")
            return True
        else:
            logger.warning(f"Failed to delete entity with ID {entity_id} from table '{table}' - entity may not exist")
            return False

    except RepositoryNotFoundError as e:
        logger.error(f"Repository not found for table '{table}': {e}")
        return False
    except UndefinedTable as e:
        logger.error(f"Table '{table}' not found: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error deleting entity from table '{table}' with ID {entity_id}: {e}", exc_info=True)
        raise
        