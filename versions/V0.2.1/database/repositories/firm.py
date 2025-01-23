from typing import Optional
from database.repositories.base import BaseRepository
from database.models import FirmModel

import logging

logger = logging.getLogger(__name__)

class FirmRepository(BaseRepository):
    """Repository for firm-specific operations."""
    
    def __init__(self, db_conn):
        """Initialize the repository with the FirmModel."""
        super().__init__(db_conn, table_name='firm', model=FirmModel)
        
    def add_firm(self):
        pass
    
    def delete_firm(self, id: int) -> bool:
        """
        Delete a firm by id.
        
        Args:
            id (int): The id of the firm to delete.
        """
        return super().delete(id)