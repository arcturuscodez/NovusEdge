from typing import List, Optional
from database.repositories.base import BaseRepository
from database.models import TransactionModel

import logging

logger = logging.getLogger(__name__)

class TransactionRepository(BaseRepository):
    """Repository for transaction-specific operations."""
    
    def __init__(self, db_conn):
        """Initialize the repository with the TransactionModel."""
        super().__init__(db_conn, table_name='transactions', model=TransactionModel)
        
    def add_transaction(self):
        pass
    
    def delete_transaction(self, id: int) -> bool:
        """ 
        Delete a transaction by id.
        
        Args:
            id (int): The id of the transaction to delete.
        """
        return super().delete(id)
    
    def update_transaction(self, id: int, **kwargs: dict) -> bool:
        """ 
        Update a transaction's information.
        
        Args:
            id (int): The id of the transaction to update.
            kwargs (dict): The updated information for the transaction.
        """
        return super().update(id, **kwargs)