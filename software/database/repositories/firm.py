from typing import Optional
from database.repositories.base import BaseRepository
from database.models import FirmModel
import logging

logger = logging.getLogger(__name__)

class FirmRepository(BaseRepository):
    """Repository for firm-specific operations."""
    
    def __init__(self, db_conn):
        """Initialize the repository with the FirmModel."""
        super().__init__(db_conn, table_name='FIRM', model=FirmModel)
        
    def add_firm(self, firm_name: str) -> Optional[int]:
        """ 
        Create a FirmModel instance with the provided firm_name and default values, then add it to the database.
        
        Args:
            firm_name (str): The name of the firm.
            
        Returns:
            Optional[int]: The ID of the newly added firm, or None if the operation failed.
        """
        try:
            new_firm = FirmModel(
                firm_name = firm_name,
            )
            return super().add(new_firm)

        except Exception as e:
            logger.error(f'Failed to add firm {firm_name}: {e}')
            return None
    
    def add_firm_expense(self, firm_id: int, expense: float) -> bool:
        """ 
        Create a new expense record for the firm.
        
        Args:
            firm_id (int): The ID of the firm.
            expense (float): The monthly expense.
            
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return super().add(firm_id, expense)
     
    def delete_firm(self, id: int) -> bool:
        """ 
        Delete a firm from the database.
        
        Args:
            id (int): The ID of the firm to delete.
            
        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        return super().delete(id)
        
    def get_firm(self, id: int) -> Optional[FirmModel]:
        """
        Retrieve a firm by ID.
        
        Args:
            id (int): The ID of the firm to retrieve.
            
        Returns:
            Optional[FirmModel]: The firm entity, or None if not found.
        """
        return super().get_entity(id=id)
    
    def update_firm(self, id: int, **kwargs: dict) -> bool:
        """
        Update a firm's information.
        
        Args:
            id (int): The ID of the firm to update.
            **kwargs: The updated information for the firm.
        """
        return super().update(id, **kwargs)