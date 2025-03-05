from typing import Optional
from database.repositories.base import BaseRepository
from database.models import TransactionModel
from decimal import Decimal

import logging

logger = logging.getLogger(__name__)

class TransactionRepository(BaseRepository):
    """Repository for transaction-specific operations."""
    
    def __init__(self, db_conn):
        """Initialize the repository with the TransactionModel."""
        super().__init__(db_conn, table_name='transactions', model=TransactionModel)
        
    def create_transaction(self, ticker: str, shares: float, price_per_share: float,
                      transaction_type: str, cost_basis: float = None,
                      realized_profit_loss: float = None, transaction_fees: float = None,
                      portion_of_position: float = None, notes: str = None) -> Optional[int]:
        """
        Create a new transaction with enhanced profit/loss tracking.

        Args:
            ticker (str): The ticker symbol of the asset.
            shares (float): The number of shares in the transaction.
            price_per_share (float): The price per share.
            transaction_type (str): Type of transaction ('buy' or 'sell').
            cost_basis (float, optional): The cost basis per share (for sells).
            realized_profit_loss (float, optional): The realized profit/loss (for sells).
            transaction_fees (float, optional): Any transaction fees.
            portion_of_position (float, optional): Percentage of position sold.
            notes (str, optional): Additional transaction notes.

        Returns:
            Optional[int]: The ID of the newly created transaction or None if failed.
        """
        try:
            transaction = TransactionModel(
                ticker=ticker.upper(),
                shares=Decimal(str(abs(shares))),
                price_per_share=Decimal(str(price_per_share)),
                transaction_type=transaction_type.lower(),
                cost_basis=Decimal(str(cost_basis)) if cost_basis is not None else None,
                realized_profit_loss=Decimal(str(realized_profit_loss)) if realized_profit_loss is not None else None,
                transaction_fees=Decimal(str(transaction_fees)) if transaction_fees is not None else None,
                portion_of_position=Decimal(str(portion_of_position)) if portion_of_position is not None else None,
                notes=notes
            )

            transaction_id = self.create(transaction)
            if transaction_id:
                logger.info(f"Created transaction: {transaction_type} {shares} shares of {ticker} at ${price_per_share}")
            else:
                logger.error(f"Failed to create {transaction_type} transaction for {ticker}")

            return transaction_id

        except Exception as e:
            logger.error(f"Transaction creation failed: {e}")
            return None
    
    def get_transactions_for_ticker(self, ticker: str, limit=None) -> list:
        """
        Get all transactions for a specific ticker, with optional limit.
        
        Returns:
            list: A list of transactions for the specified ticker.
        """
        return self.get_all(ticker=ticker.upper(), order_by="transaction_date DESC", limit=limit)
    
    def get_realized_profit_loss_history(self, ticker=None) -> list:
        """ 
        Get realized profit/loss history, optionally filtered by ticker.
        
        Returns:
            list: A list of realized profit/loss transactions.
        """
        conditions = {'transaction_type': 'sell'}
        if ticker: 
            conditions['ticker'] = ticker.upper()
            
        return self.get_all(**conditions, order_by="transaction_date DESC")
    
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