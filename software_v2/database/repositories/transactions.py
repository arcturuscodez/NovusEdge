from typing import List, Optional
from database.repositories.base import BaseRepository
from database.repositories.portfolio import PortfolioRepository
from database.models import TransactionsModel

import logging

logger = logging.getLogger(__name__)

class TransactionsRepository(BaseRepository):
    """Repository for Transaction-specific operations."""
    
    VALID_TRANSACTION_TYPES = {'buy', 'sell'}
    
    def __init__(self, db_conn):
        """Initialize the repository with the TransactionsModel."""
        super().__init__(db_conn, table_name='transactions', model=TransactionsModel)
        
    def add_transaction(self, ticker: str, shares: int, pps: float, transaction_type: str, firm_id: int = 1) -> Optional[int]:
        """ 
        Add a new transaction to the database.
        
        Args:
            firm_id (int): ID of the firm to add a transaction to.
            ticker (str): Ticker symbol of the asset.
            shares (int): Number of shares.
            pps (float): Price per share.
            total (float): Total cost of the transaction.
            transaction_type (str): Type of transaction (buy/sell).
            
        Returns:
            Optional[int]: The id of the newly added transaction, or None if failed.
        """
        if transaction_type.lower() not in self.VALID_TRANSACTION_TYPES:
            logger.error(f'Invalid transaction type: {transaction_type}')
            return None
        
        try:
            new_transaction = TransactionsModel(
                firm_id=firm_id,
                id=None,
                ticker=ticker,
                shares=shares,
                price_per_share=pps,
                transaction_type=transaction_type
            )
            transaction_id = super().add(new_transaction)
            if transaction_id and transaction_type.lower() == 'buy':
                portfolio_repo = PortfolioRepository(self.db)
                portfolio_repo.add_asset(firm_id, ticker, shares)
            elif transaction_id and transaction_type.lower() == 'sell':
                portfolio_repo = PortfolioRepository(self.db)
                asset = portfolio_repo.get_asset_by_ticker(firm_id, ticker)
                if asset:
                    updated_shares = asset.shares - shares
                    if updated_shares < 0:
                        logger.error(f'Cannot sell more shares than available: {shares} > {asset.shares}')
                        return None
                    portfolio_repo.edit_asset_shares(firm_id, ticker, shares=updated_shares)
            return transaction_id, super().add(new_transaction)
        
        except Exception as e:
            logger.error(f'Failed to add transaction: {e}')
            return None
    
    def get_all_transactions(self) -> List[TransactionsModel]:
        """Retrieve all transactions."""
        return super().fetch_all()
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction by id."""
        return super().delete(transaction_id)
    
    def edit_transaction(self, transaction_id, **kwargs):
        """
        Edit a specific field of a transaction.
        
        Args:
            transaction_id (int): ID of the transaction to edit.
            **kwargs: Key-value pairs of fields to update.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        return super().edit(transaction_id, **kwargs)
    
    def update_transaction(self):
        pass