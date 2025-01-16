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
        
    def add_transaction(self, ticker, shares, price_per_share, transaction_type) -> Optional[int]:
        """ 
        Add a new transaction to the TRANSACTIONS table.
        
        Args:
            ticker (str): Ticker symbol of the asset.
            shares (float): The acquired number of asset/shares.
            price_per_share (float): The price per individual asset/shares.
            transaction_type (str): The type of transaction (buy/sell).
        """
        try:
            if transaction_type.lower() not in 'buy' or 'sell':
                logger.error(f'Transaction type must be either "buy" or "sell". Detected: {transaction_type}')
                raise ValueError('Transaction type must be either "buy" or "sell".')
            
            new_transaction = TransactionModel(
                id=None,
                ticker=ticker,
                shares=shares,
                price_per_share=price_per_share,
                transaction_type=transaction_type
            )
            return super().add(new_transaction)
        
        except Exception as e:
            logger.error(f'Failed to add a transaction: {e}')
            return None
        
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