from typing import Optional
from decimal import Decimal
from database.repositories.base import BaseRepository
from database.repositories.transaction import TransactionRepository
from database.models import PortfolioModel

import logging

logger = logging.getLogger(__name__)

class PortfolioRepository(BaseRepository):
    """Repository for portfolio-specific operations."""
    
    def __init__(self, db_conn):
        """Initialize the repository with the PortfolioModel."""
        super().__init__(db_conn, table_name='portfolio', model=PortfolioModel)
        
    def create_or_update_asset(self, ticker: str, shares: Decimal, price_per_share: Decimal,
                      transaction_type: str = 'buy', transaction_fees: float = 0.0, 
                      existing_transaction_id: int = None) -> bool:
        """
        Add or update an asset in the portfolio with improved profit/loss tracking.

        Args:
            ticker (str): The ticker symbol of the asset.
            shares (Decimal): The number of shares to add/remove.
            price_per_share (Decimal): The price per share.
            transaction_type (str): The type of transaction ('buy' or 'sell').
            transaction_fees (float): Any transaction fees.
            existing_transaction_id (int, optional): ID of an existing transaction.

        Returns:
            bool: True if the asset was added or updated successfully.
        """
        ticker = ticker.upper()
        shares_decimal = Decimal(str(abs(shares)))
        price_per_share_decimal = Decimal(str(price_per_share))
        transaction_value = shares_decimal * price_per_share_decimal
        is_buy = transaction_type.lower() == 'buy'
        actual_shares = shares_decimal if is_buy else -shares_decimal

        try:
            # Get existing asset or create new one
            asset = self.get_entity(ticker=ticker)

            # CASE 1: New asset
            if not asset:
                if not is_buy:
                    logger.error(f"Cannot sell asset {ticker} that does not exist in portfolio")
                    return False

                # Create new portfolio entry
                new_asset = PortfolioModel(
                    ticker=ticker,
                    total_shares=actual_shares,
                    total_invested=transaction_value,
                    average_purchase_price=price_per_share_decimal,
                    current_price=price_per_share_decimal,
                    realized_profit_loss=Decimal('0')
                )

                asset_id = self.create(new_asset)
                if asset_id:
                    logger.info(f"Created portfolio entry for {ticker}: {actual_shares} shares at ${price_per_share_decimal}")
                    return True
                return False

            # CASE 2: Update existing asset
            new_shares = asset.total_shares + actual_shares

            # Validate: Can't sell more than owned
            if new_shares < 0:
                logger.error(f"Cannot sell {shares_decimal} shares of {ticker}, only {asset.total_shares} available")
                return False

            # Calculate fields for update
            update_fields = {}
            realized_profit_loss = Decimal('0')

            if is_buy:
                # BUY: Update average price via weighted average
                new_total_invested = asset.total_invested + transaction_value
                new_average_price = new_total_invested / new_shares if new_shares > 0 else asset.average_purchase_price

                update_fields = {
                    'total_shares': new_shares,
                    'total_invested': new_total_invested,
                    'average_purchase_price': new_average_price,
                    'current_price': price_per_share_decimal
                }
            else:
                # SELL: Calculate realized profit/loss
                cost_basis = asset.average_purchase_price
                portion_sold = shares_decimal / asset.total_shares
                realized_profit_loss = (price_per_share_decimal - cost_basis) * shares_decimal
                investment_reduction = asset.total_invested * portion_sold

                update_fields = {
                    'total_shares': new_shares,
                    'total_invested': asset.total_invested - investment_reduction,
                    'realized_profit_loss': asset.realized_profit_loss + realized_profit_loss,
                    'current_price': price_per_share_decimal
                }

                # Update transaction with profit/loss details if ID provided
                if existing_transaction_id:
                    transaction_repo = TransactionRepository(self.db)
                    transaction_repo.update(existing_transaction_id, 
                        cost_basis=cost_basis,
                        realized_profit_loss=realized_profit_loss,
                        portion_of_position=portion_sold * 100,
                        notes=f"Selling {portion_sold:.2%} of position"
                    )

            # Apply update
            success = self.update(asset.id, **update_fields)
            if success:
                logger.info(f"Updated {ticker}: {new_shares} shares, total invested: ${update_fields['total_invested']}")
            return success

        except Exception as e:
            logger.error(f"Failed to update asset {ticker}: {e}")
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
        Retrieve an asset entity by id.
        
        Args:
            id (int): The id of the asset entity to retrieve.    
        """
        return super().get_entity(ticker=ticker)