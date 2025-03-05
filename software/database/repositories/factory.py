from typing import Type
from database.connection import DatabaseConnection
from database.repositories.shareholder import ShareholderRepository
from database.repositories.transaction import TransactionRepository
from database.repositories.portfolio import PortfolioRepository
from database.repositories.firm import FirmRepository
from database.repositories.task import TaskRepository

import logging

logger = logging.getLogger(__name__)

class RepositoryNotFoundError(Exception):
    """Exception raised when the repository is not found."""
    pass

REPOSITORY_MAP = {
    'SHAREHOLDERS': ShareholderRepository,
    'TRANSACTIONS': TransactionRepository,
    'PORTFOLIO': PortfolioRepository,
    'FIRM': FirmRepository,
    'TASK_METADATA': TaskRepository
}

def register_repository(table_name: str, repository_class: Type):
    """Register a new repository to the REPOSITORY_MAP."""
    try:
        table_name_upper = table_name.upper()
        logger.debug(f"Registering repository for table: {table_name_upper} with class {repository_class.__name__}")
        REPOSITORY_MAP[table_name_upper] = repository_class
        logger.info(f"Successfully registered repository for table: {table_name_upper}")
    except Exception as e:
        logger.error(f"Failed to register repository for table '{table_name}': {e}", exc_info=True)
        raise

def get_repository(table_name: str, db_conn: DatabaseConnection) -> Type:
    """
    Retrieve an instance of the repository based on the table name.

    Args:
        table_name (str): The name of the table.
        db_conn (DatabaseConnection): The database connection instance.

    Returns:
        An instance of the corresponding repository.
    
    Raises:
        RepositoryNotFoundError: If the repository for the given table is not found.
    """
    try:
        table_name_upper = table_name.upper()
        logger.debug(f"Attempting to retrieve repository for table: {table_name_upper}")
        
        repository_class = REPOSITORY_MAP.get(table_name_upper)
        if repository_class:
            logger.debug(f"Retrieved repository for table: {table_name_upper}")
            return repository_class(db_conn)
        
        logger.error(f"Repository for table '{table_name_upper}' not found in REPOSITORY_MAP")
        if RepositoryNotFoundError:
            logger.error(f"RepositoryNotFoundError: {RepositoryNotFoundError}")

    except RepositoryNotFoundError as e:
        logger.error(f"Error retrieving repository: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving repository for table '{table_name}': {e}", exc_info=True)
        raise