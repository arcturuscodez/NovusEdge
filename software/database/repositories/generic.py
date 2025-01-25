from database.repositories.base import BaseRepository
from database.models import GenericModel
from database.connection import DatabaseConnection

import logging 

logger = logging.getLogger(__name__)

class GenericRepository(BaseRepository):
    """
    Repository for generic operations across any table.
    """
    def __init__(self, db_conn: DatabaseConnection, table_name: str):
        """Initialize the GenericRepository with a specified table."""
        super().__init__(db_conn, table_name=table_name, model=GenericModel)