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
        
    def add_asset(self, ticker, shares) -> Optional[int]:
        """ 
        Add a new asset to the portfolio table.
        
        Args:
            ticker (str): Ticker symbol of the asset.
            shares (int): Number of shares.
        Returns:
            Optional[int]: The id of the newly added asset, or None if failed.
        """
        if not ticker or not shares:
            logger.error('Invalid asset data provided.')
            return None
        
        try:
            new_asset = PortfolioModel(
                id=None,
                ticker=ticker,
                shares=shares
            )
            return super().add(new_asset)
        except Exception as e:
            logger.error(f'Failed to add asset: {e}')
            return None
    
    def get_all_assets(self) -> List[PortfolioModel]:
        """Retrieve all assets inside the portfolio."""
        return super().fetch_all()
    
    def delete_asset(self, asset_id: int) -> bool:
        """Delete an asset by ID."""
        return super().delete(asset_id)

    def edit_asset(self, asset_id: int, **kwargs) -> bool:
        """
        Edit a specific field of an asset.
        
        Args:
            asset_id (int): ID of the asset to edit.
            **kwargs: Key-value pairs of fields to update.
        
        Returns:
            bool: True if edit was successful, False otherwise.
        """
        return super().edit(asset_id, **kwargs)        