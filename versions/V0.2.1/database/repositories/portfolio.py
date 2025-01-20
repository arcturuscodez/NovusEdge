from typing import List, Optional 
from database.repositories.base import BaseRepository
from database.models import PortfolioModel

import logging

logger = logging.getLogger(__name__)

class PortfolioRepository(BaseRepository):
    """Repository for portfolio-specific operations."""
    
    def __init__(self, db_conn):
        """Initialize the repository with the PortfolioModel."""
        super().__init__(db_conn, table_name='portfolio', model=PortfolioModel)
        
    def add_or_update_asset(self, ticker: str, shares: float) -> bool:
        """ 
        Add a new asset or update existing asset's shares in the PORTFOLIO table.
        
        Args:
            ticker (str): Ticker symbol of the asset.
            shares (float): The acquired number of asset/shares.
        """
        try:
            asset = self.get(ticker=ticker)
            if asset:
                new_shares = asset.shares + shares
                if new_shares < 0:
                    logger.warning('Insufficient shares to sell.')
                    return False
                return self.update(asset.id, shares=new_shares)
            else:
                new_asset = PortfolioModel(
                    id=None,
                    ticker=ticker,
                    shares=shares
                )
                return self.add(new_asset) is not None
    
        except Exception as e:
            logger.error(f'Failed to add/update asset: {e}')
            return False