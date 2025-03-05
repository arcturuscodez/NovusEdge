from typing import List, Optional
from database.repositories.base import BaseRepository
from database.models import ShareholderModel

import logging

logger = logging.getLogger(__name__)

class ShareholderRepository(BaseRepository):
    """Repository for shareholder-specific operations."""
    
    def __init__(self, db_conn):
        """Initialize the repository with the ShareholderModel."""
        super().__init__(db_conn, table_name='shareholders', model=ShareholderModel)
    
    def create_shareholder(self, name: str, ownership: float, investment: float, email: str) -> Optional[int]:
        """ 
        Create a new shareholder entity.
        
        Args:
            name (str): Name of the shareholder.
            ownership (float): Ownership percentage.
            investment (float): Investment amount.
            email (str): Shareholder's email.
        
        Returns:
            Optional[int]: The ID of the newly created shareholder, or None if failed.
        """
        try:
            new_shareholder = ShareholderModel(
                id=None,
                name=name.lower(), # Force shareholder name to be lowercase to avoid duplicates by case insensitivity
                ownership=ownership,
                investment=investment,
                email=email
            )
            return super().create(new_shareholder)

        except Exception as e:
            logger.error(f'Failed to create shareholder: {e}')
            return None
        
    def delete_shareholder(self, id: int) -> bool:
        """
        Delete a shareholder by id.
        
        Args:
            id (int): The id of the shareholder to delete.
        """
        return super().delete(id)
    
    def update_shareholder(self, id: int, **kwargs: dict) -> bool:
        """
        Update a shareholder's information.
        
        Args:
            id (int): The id of the shareholder to update.
            kwargs (dict): The updated information for the shareholder.
        """
        return super().update(id, **kwargs)