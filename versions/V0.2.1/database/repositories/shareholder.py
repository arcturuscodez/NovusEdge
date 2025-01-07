from typing import List, Optional
from database.repositories.base import BaseRepository
from database.models import ShareholderModel
import logging

class ShareholderRepository(BaseRepository):
    """Repository for shareholder-specific operations."""
    
    def __init__(self, db_conn):
        """Initialize the repository with the ShareholderModel."""
        super().__init__(db_conn, table_name='shareholders, model=ShareholderModel')
    
    def add_shareholder(self, name: str, ownership: float, investment: float, email: str) -> Optional[int]:
        """ 
        Add a new shareholder to the database.
        
        Args:
            name (str): Name of the shareholder.
            ownership (float): Ownership percentage.
            investment (float): Investment amount.
            email (str): Shareholder's email.
        
        Returns:
            Optional[int]: The ID of the newly added shareholder, or None if failed.
        """
        pass