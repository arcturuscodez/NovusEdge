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
            if asset:
                new_shares = asset.total_shares + shares
                if new_shares < 0:
                    logger.warning(f'Insufficient shares of {ticker} to sell. Current shares {asset.total_shares}')
                    return False
                elif new_shares == 0:
                    success = self.delete_asset(asset.id)
                    if success:
                        logger.info(f'All shares of {ticker} sold. Portfolio entry deleted.')
                        return True
                    else:
                        logger.error(f'Failed to delete portfolio entry for {ticker}.')
                        return False
                
                update_fields = {'total_shares': new_shares}
                
                if transaction_type.lower() == 'buy':
                    update_fields['total_invested'] = asset.total_invested + (shares * price_per_share)
                elif transaction_type.lower() == 'sell':
                    avg_cost_per_share = asset.total_invested / asset.total_shares # Should maybe be in the table.
                    realized_pl = (price_per_share - avg_cost_per_share) * abs(shares)
                    update_fields['realized_profit_loss'] = asset.realized_profit_loss + realized_pl
                    update_fields['total_invested'] = asset.total_invested - (avg_cost_per_share * abs(shares))
                        
                success = self.update(asset.id, **update_fields)
                if success:
                    logger.info(f'Asset {ticker} updated successfully.')
                return success
            else:
                if transaction_type.lower() == 'sell':
                    logger.warning(f'No shares of {ticker} to sell.')
                    return False
                
                new_asset = PortfolioModel(
                    id = None,
                    ticker=ticker,
                    total_shares=shares,
                    total_invested=shares * price_per_share,
                    realized_profit_loss=Decimal('0.00'),
                )
                success = self.add(new_asset) is not None
                if success:
                    logger.info(f'Asset {ticker} added successfully.')
                return success
            
        except (InvalidOperation, ValueError) as e:
            logger.error(f'Invalid numerical value provided: {e}.')
            return False
                    
    def delete_asset(self, id: int) -> bool:
        """ 
        Delete an asset by id.
        
        Args:
            id (int): The id of the asset to delete.
        """
        return super().delete(id)
    
    def get_asset_by_ticker(self, ticker: str) -> Optional[PortfolioModel]:
        """ 
        Retrieve an asset by id.
        
        Args:
            id (int): The id of the asset to retrieve.    
        """
        return super().get_entity(ticker=ticker)