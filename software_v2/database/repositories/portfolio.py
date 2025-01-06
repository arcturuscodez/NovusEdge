from typing import List, Optional
from database.repositories.base import BaseRepository
from database.models import PortfolioModel

import logging 

logger = logging.getLogger(__name__)

class PortfolioRepository(BaseRepository):
    """Repository for Portfolio-specific operations."""
    
    def __init__(self, db_conn):
        """Initialize the repository with the PortfolioModel."""
        super().__init__(db_conn, table_name='portfolio', model=PortfolioModel)
        
    def add_asset(self, firm_id: int, ticker: str, shares: int) -> bool:
        """ 
        Add a new asset to the portfolio table.
        
        Args:
            firm_id (int): ID of the firm.
            ticker (str): Ticker symbol of the asset.
            shares (int): Number of shares.
        
        Returns:
            bool: True if added successfully, False otherwise.
        """
        try:
            # Insert fetch live stock data here
            new_asset = PortfolioModel(
                firm_id=firm_id,
                ticker=ticker,
                shares=shares
            )
            return super().add(new_asset) is not None
        except Exception as e:
            logger.error(f'Failed to add asset: {e}')
            return False
    
    def get_all_assets(self) -> List[PortfolioModel]:
        """Retrieve all assets inside the portfolio."""
        return super().fetch_all()
    
    def get_asset_by_ticker(self, firm_id: int, ticker: str) -> List[PortfolioModel]:
        """Retrieve a single asset by its ticker symbol."""
        return super().get(firm_id=firm_id, ticker=ticker)
    
    def delete_asset(self, asset_id: int) -> bool:
        """Delete an asset by ID."""
        return super().delete(asset_id)
    
    def edit_asset_shares(self, firm_id: int, ticker: str, shares: int) -> bool:
        """ 
        Update the number of shares for a specific asset.
        
        Args:
            firm_id (int): ID of the firm.
            ticker (str): Ticker symbol of the asset.
            shares (int): New number of shares.
        Returns:
            bool: True if updated successfully, False otherwise.    
        """
        return super().edit(entity_id=firm_id, ticker=ticker, shares=shares)