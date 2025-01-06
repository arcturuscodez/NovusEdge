from typing import List, Optional
from database.repositories.base import BaseRepository
from database.models import ShareholderModel
import logging

logger = logging.getLogger(__name__)

class ShareholderRepository(BaseRepository):
    """Repository for Shareholder-specific operations."""

    def __init__(self, db_conn):
        """Initialize the repository with the ShareholderModel."""
        super().__init__(db_conn, table_name='shareholders', model=ShareholderModel)

    def add_shareholder(self, name: str, ownership: float, investment: float, email: str, shareholder_status: Optional[str] = None) -> Optional[int]: 
        
        # Can shareholder status be removed? Should be handled by the database like timestamp.
        
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
        try:
            new_shareholder = ShareholderModel(
                id=None,
                name=name,
                ownership=ownership,
                investment=investment,
                email=email,
                shareholder_status=shareholder_status
            )
            return super().add(new_shareholder)
        except Exception as e:
            logger.error(f"Failed to add shareholder: {e}")
            return None

    def get_all_shareholders(self) -> List[ShareholderModel]:
        """Retrieve all shareholders."""
        return super().fetch_all()
    
    def delete_shareholder(self, shareholder_id: int) -> bool:
        """Delete a shareholder by ID."""
        return super().delete(shareholder_id)
    
    def edit_shareholder(self, shareholder_id: int, **kwargs) -> bool:
        """
        Edit a specific field of a shareholder.
        
        Args:
            shareholder_id (int): ID of the shareholder to edit.
            **kwargs: Key-value pairs of fields to update.
        
        Returns:
            bool: True if edit was successful, False otherwise.
        """
        return super().edit(shareholder_id, **kwargs)
    
    def update_shareholder(self):
        pass