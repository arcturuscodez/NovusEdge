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
        
    def add_or_update_asset(self, ticker: str, shares: float, total_invested: float, **kwargs) -> bool:
        """ 
        Add a new asset or update existing asset's shares and other fields in the PORTFOLIO table.
        
        Args:
            ticker (str): Ticker symbol of the asset.
            shares (float): The number of asset/shares to add/remove or update.
            total_invested (float): The total amount invested in the asset.
            **kwargs: Additional fields to update in the asset. (e.g., current_price, dividend_yield, etc...)
        """
        try:
            asset = self.get(ticker=ticker)
            if asset:
                new_shares = asset.total_shares + shares
                if new_shares < 0:
                    logger.warning('Insufficient shares to sell.')
                    return False
                
                update_fields = {'total_shares': new_shares}
                update_fields.update(kwargs)
                return self.update(asset.id, **update_fields) 
            else:
                new_asset = PortfolioModel(
                    id=None,
                    ticker=ticker,
                    total_shares=shares,
                    total_invested=total_invested,
                    **kwargs 
                )   
                return self.add(new_asset) is not None
            
        except Exception as e:
            logger.error(f'Failed to add or update asset: {e}')
            return False
                    
    def delete_asset(self, id: int) -> bool:
        """ 
        Delete an asset by id.
        
        Args:
            id (int): The id of the asset to delete.
        """
        return super().delete(id)
    
    def get_asset(self, id: int) -> Optional[PortfolioModel]:
        """ 
        Retrieve an asset by id.
        
        Args:
            id (int): The id of the asset to retrieve.    
        """
        return super().get(id=id)
        