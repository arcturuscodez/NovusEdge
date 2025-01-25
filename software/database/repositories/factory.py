from typing import Type, Optional
from database.connection import DatabaseConnection
from database.repositories.shareholder import ShareholderRepository
from database.repositories.transaction import TransactionRepository
from database.repositories.portfolio import PortfolioRepository
from database.repositories.firm import FirmRepository

import logging

logger = logging.getLogger(__name__)

class RepositoryNotFoundError(Exception):
    """Exception raised when the repository is not found."""
    pass

REPOSITORY_MAP = {
    'SHAREHOLDERS': ShareholderRepository,
    'TRANSACTIONS': TransactionRepository,
    'PORTFOLIO': PortfolioRepository,
    'FIRM': FirmRepository
}

def register_repository(table_name: str, repository_class: Type):
    """Register a new repository to the REPOSITORY_MAP."""
    REPOSITORY_MAP[table_name.upper()] = repository_class
    logger.debug(f'Registered repository for table: {table_name.upper()}')
    
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
    repository_class = REPOSITORY_MAP.get(table_name.upper())
    if repository_class:
        logger.info(f'Retrieving repository for table: {table_name.upper()}')
        return repository_class(db_conn)
    else:
        logger.error(f"Repository for table '{table_name}' not found.") 
        raise RepositoryNotFoundError(f"Repository for table '{table_name}' not found.")