from typing import Optional
from decimal import Decimal, InvalidOperation
from database.repositories.base import BaseRepository
from database.models import PortfolioModel

import logging

logger = logging.getLogger(__name__)

class PortfolioRepository(BaseRepository):
    """Repository for portfolio-specific operations."""
    
    def __init__(self, db_conn):
        """Initialize the repository with the PortfolioModel."""
        super().__init__(db_conn, table_name='portfolio', model=PortfolioModel)
        
    def add_or_update_asset(self, ticker: str, shares: Decimal, price_per_share: Decimal, transaction_type: str) -> bool:
        """ 
        Add a new asset or update existing asset's shares and other fields in the PORTFOLIO table.
        
        Args:
            ticker (str): Ticker symbol of the asset
            shares (Decimal): The number of asset/shares to add/remove or update.
            price_per_share (Decimal): The price per share of the asset.
            transaction_type (str): Type of transaction ('buy' or 'sell').
        """
        try:
            asset = self.get_asset_by_ticker(ticker)
            is_buy = transaction_type == 'buy'
            
            if asset: 
                new_shares = asset.total_shares + (shares if is_buy else -shares)
                
                if new_shares < 0:
                    logger.warning(f'Insufficient shares to sell: {shares} requested, {asset.total_shares} available.')
                    return False
                
                update_fields = {
                    'total_shares': new_shares,
                    'total_invested': asset.total_invested + (shares * price_per_share if is_buy else 0),
                    'realized_profit_loss': asset.realized_profit_loss + (
                        0 if is_buy else (price_per_share - (asset.total_invested / asset.total_shares)) * abs(shares)
                    ),
                }
                
                if new_shares == 0:
                    if self.delete_asset(asset.id):
                        logger.info(f'All shares of {ticker} sold. Entry deleted.')
                        return True
                    
                    logger.warning(f'Failed to delete {ticker} from portfolio.')
                    return False
                
                success = self.update(asset.id, **update_fields)
                logger.info(f'Asset {ticker} {"updated" if success else "update failed"}.')
                return success
        
            if is_buy:
                new_asset = PortfolioModel(
                    id=None, 
                    ticker=ticker,
                    total_shares=shares,
                    total_invested=shares * price_per_share,
                    realized_profit_loss=Decimal('0.00'),
                )
                success = self.create(new_asset) is not None
                logger.info(f'Asset {ticker} created successfully.' if success else f'Failed to add {ticker}.')
                return success
            
            logger.warning(f'No shares of {ticker} to sell.')
            return False
        
        except (InvalidOperation, ValueError) as e:
            logger.error(f'Invalid numerical value: {e}')
            return False
        
    def delete_asset(self, id: int) -> bool:
        """ 
        Delete an asset by id.
        
        Args:
            id (int): The id of the asset to delete.
        """
        return super().delete(id)
    
    def update_asset(self, id: int, **kwargs) -> bool:
        """ 
        Update an asset by id.
        
        Args:
            id (int): The id of the asset to update.
            **kwargs: The fields to update.
        """
        return super().update(id, **kwargs)
    
    def get_asset_by_ticker(self, ticker: str) -> Optional[PortfolioModel]:
        """ 
        Retrieve an asset by id.
        
        Args:
            id (int): The id of the asset to retrieve.    
        """
        return super().get_entity(ticker=ticker)