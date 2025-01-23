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
            # Instantiate FirmModel with firm_name; other fields use default values
            new_firm = FirmModel(
                firm_name=firm_name
                # Other fields are automatically set to their default values
            )
            
            # Add the firm to the database
            firm_id = self.add(new_firm)
            
            if firm_id:
                logger.info(f'Firm "{new_firm.firm_name}" added successfully with ID {firm_id}.')
            return firm_id
        except Exception as e:
            logger.error(f'Error adding firm "{firm_name}": {e}')
            return None
        
    def update_firm(self, firm_id: int, assets: float, cash: float, profit_loss: float) -> bool:
        """ 
        Update specific fields of a firm.
        
        Args:
            firm_id (int): The ID of the firm to update.
            assets (float): The total assets value.
            cash (float): The total cash value.
            profit_loss (float): The total profit or loss.
            
        Returns:
            bool: True if the update was successful, False otherwise.
        """
        try:
            capital = assets + cash
            success = self.update(firm_id, assets=assets, cash=cash, capital=capital, profit_loss=profit_loss)
            if success:
                logger.info(f'Firm ID {firm_id} updated with Assets={assets}, Cash={cash}, Capital={capital}, Profit_Loss={profit_loss}.')
            return success
        except Exception as e:
            logger.error(f'Error updating firm ID {firm_id}: {e}')
            return False
        
    def delete_firm(self, firm_id: int) -> bool:
        """ 
        Delete a firm from the database.
        
        Args:
            firm_id (int): The ID of the firm to delete.
            
        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        return super().delete(firm_id)
        
    def get_firm(self, firm_id: int) -> Optional[FirmModel]:
        """
        Retrieve a firm by ID.
        
        Args:
            firm_id (int): The ID of the firm to retrieve.
            
        Returns:
            Optional[FirmModel]: The firm entity, or None if not found.
        """
        return super().get_entity(firm_id)

    def update_capital(self, firm_id: int, assets: float, cash: float) -> bool:
        """
        Update the CAPITAL field based on ASSETS and CASH.
        
        Args:
            firm_id (int): The ID of the firm to update.
            assets (float): The total assets value.
            cash (float): The total cash value.
        
        Returns:
            bool: True if update was successful, False otherwise.
        """
        try:
            capital = assets + cash
            profit_loss = self.get_firm(firm_id).profit_loss if self.get_firm(firm_id) else 0.0
            success = self.update_firm(firm_id, assets=assets, cash=cash, profit_loss=profit_loss)
            if success:
                logger.info(f'Capital updated for Firm ID {firm_id}: Assets={assets}, Cash={cash}, Capital={capital}.')
            return success
        except Exception as e:
            logger.error(f'Failed to update capital for Firm ID {firm_id}: {e}')
            return False