from typing import Optional
from database.connection import DatabaseConnection
from database.repositories.shareholder import ShareholderRepository

REPOSITORY_MAP = {
    'SHAREHOLDERS': ShareholderRepository
}

def get_repository(table_name: str, db_conn: DatabaseConnection):
    """ 
    Retrieve an instance of the repository based on the table name.
    """
    repository_class = REPOSITORY_MAP.get(table_name.upper())
    if repository_class:
        return repository_class(db_conn)
    return None