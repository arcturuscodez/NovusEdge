"""Service module for handling the deletion of an entity from a table."""
from psycopg2.errors import UndefinedTable
from database.repositories.factory import RepositoryNotFoundError
from database.repositories.base import GenericRepository
from database.repositories.shareholder import ShareholderRepository
from database.repositories.transaction import TransactionRepository
from database.repositories.firm import FirmRepository
from database.repositories.portfolio import PortfolioRepository
from database.connection import DatabaseConnection
from decimal import Decimal

import logging

logger = logging.getLogger(__name__)

def handle_delete_by_id(db: DatabaseConnection, table: str, entity_id: int) -> bool:
    """
    Handle the deletion of an entity from a table by ID.
    
    Special handling is implemented for some entities like shareholders.

    Args:
        db (DatabaseConnection): The database connection object.
        table (str): The name of the table to delete from.
        entity_id (int): The ID of the entity to delete.

    Returns:
        bool: True if the entity was deleted successfully, False otherwise.
    """
    try:
        if not table:
            logger.error("Table name not provided for deletion")
            return False

        if not isinstance(entity_id, int):
            logger.error(f"Entity ID must be an integer, got {type(entity_id)}")
            return False

        if table.upper() == 'SHAREHOLDERS':
            logger.debug(f'Used specialized handler for shareholder deletion (ID: {entity_id})')
            return handle_delete_shareholder(db, entity_id)
        
        logger.debug(f"Attempting to delete entity ID {entity_id} from table '{table}'")
        repository = GenericRepository(db, table)
        result = repository.delete(entity_id)

        if result:
            logger.info(f"Entity with ID {entity_id} from table '{table}' deleted successfully")
            return True
        else:
            logger.warning(f"Failed to delete entity with ID {entity_id} from table '{table}' - entity may not exist")
            return False

    except RepositoryNotFoundError as e:
        logger.error(f"Repository not found for table '{table}': {e}")
        return False
    except UndefinedTable as e:
        logger.error(f"Table '{table}' not found: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error deleting entity from table '{table}' with ID {entity_id}: {e}", exc_info=True)
        raise
    
def handle_delete_shareholder(db: DatabaseConnection, shareholder_id: int) -> bool:
    """
    Handle the deletion of a shareholder and all associated transactions.
    """
    try:
        db.connection.autocommit = False
        
        # 1-3. Get the shareholder, firm data, and calculate ownership percentage
        shareholder_repo = ShareholderRepository(db)
        shareholder = shareholder_repo.get_entity(id=shareholder_id)
        if not shareholder:
            logger.warning(f'Shareholder with ID {shareholder_id} not found')
            return False
        
        logger.info(f'Processing withdrawal for shareholder {shareholder.name} (ID: {shareholder.id})')
        
        firm_repo = FirmRepository(db)
        firm = firm_repo.get_entity(id=1)  # TODO: Make firm ID dynamic
        if not firm:
            logger.error('Firm data not found')
            db.manual_rollback(db.connection)
            return False
        
        ownership_proportion = Decimal(str(shareholder.ownership / 100))
        
        # 4. Get all portfolio assets
        portfolio_repo = PortfolioRepository(db)
        assets = portfolio_repo.get_all()
        
        # 5. Process each asset - ALWAYS ROUND TO WHOLE SHARES
        transaction_repo = TransactionRepository(db)
        
        logger.info(f'Shareholder owns {shareholder.ownership}% of the firm assets')
        total_liquidation_value = Decimal('0')
        total_asset_value_reduction = Decimal('0')
        
        for asset in assets:
            if not asset.current_price or asset.total_shares == 0:
                continue
            
            # Calculate shares to liquidate and ROUND TO WHOLE SHARES
            exact_shares = Decimal(str(asset.total_shares)) * ownership_proportion
            
            # For small shareholders, ensure at least 1 share is sold if they own anything
            if exact_shares > 0 and exact_shares < 1:
                shares_to_liquidate = Decimal('1')
            else:
                # Round UP to nearest whole share - math.ceil equivalent for Decimal
                shares_to_liquidate = (exact_shares.quantize(Decimal('1'), rounding='ROUND_UP'))
                
            # Make sure we don't try to sell more shares than we have
            shares_to_liquidate = min(shares_to_liquidate, Decimal(str(asset.total_shares)))
            
            if shares_to_liquidate <= 0:
                continue
                
            logger.info(f'Liquidating {shares_to_liquidate} shares of {asset.ticker} (calculated from {exact_shares:.4f} exact shares)')
            
            # Calculate the liquidation value
            asset_liquidation_value = shares_to_liquidate * Decimal(str(asset.current_price))
            total_liquidation_value += asset_liquidation_value
            total_asset_value_reduction += asset_liquidation_value
            
            # Create a liquidation transaction with WHOLE SHARES
            transaction_id = transaction_repo.add_transaction(
                ticker=asset.ticker,
                shares=shares_to_liquidate,
                price_per_share=Decimal(str(asset.current_price)),
                transaction_type='sell'
            )
            
            if not transaction_id:
                logger.error(f'Failed to create liquidation transaction for {shares_to_liquidate} shares of {asset.ticker}')
                db.manual_rollback(db.connection)
                return False
            
            # Update portfolio - ENSURE SHARES ARE SUBTRACTED
            success = portfolio_repo.add_or_update_asset(
                ticker=asset.ticker,
                shares=-shares_to_liquidate,  # Negative shares for sell
                price_per_share=Decimal(str(asset.current_price)),
                transaction_type='sell'
            )
            
            if not success:
                logger.error(f'Failed to update portfolio for {asset.ticker}')
                db.manual_rollback(db.connection)
                return False
        
        # 6-9. Handle cash withdrawal, update firm, and complete shareholder deletion
        # Rest of the function remains similar...
        investment_to_withdraw = Decimal(str(shareholder.investment))
        
        logger.info(f'Withdrawing {investment_to_withdraw} from firm cash')
        logger.info(f'Reducing firm assets by {total_asset_value_reduction}')
        logger.info(f'Liquidation value: {total_liquidation_value}')
        
        exact_ownership_value = Decimal('0')
        for asset in assets:
            if asset.current_price and asset.total_shares > 0:
                exact_value = Decimal(str(asset.total_shares)) * ownership_proportion * Decimal(str(asset.current_price))
                exact_ownership_value += exact_value

        # Adjust cash withdrawal if significantly more shares were liquidated than mathematically owed
        if total_liquidation_value > (exact_ownership_value * Decimal('1.05')):
            logger.info(f'Adjusting cash withdrawal due to rounding to whole shares')
            logger.info(f'Exact ownership value: {exact_ownership_value}, Liquidation value: {total_liquidation_value}')
            adjustment_factor = exact_ownership_value / total_liquidation_value
            original_withdrawal = investment_to_withdraw
            investment_to_withdraw = min(investment_to_withdraw, 
                                        shareholder.investment * adjustment_factor)
            logger.info(f'Adjusted withdrawal from {original_withdrawal} to {investment_to_withdraw}')
        
        updated_cash = Decimal(str(firm.cash)) - investment_to_withdraw
        updated_assets = Decimal(str(firm.assets)) - total_asset_value_reduction
        
        firm_success = firm_repo.update_firm(1, CASH=updated_cash, ASSETS=updated_assets)
        if not firm_success:
            logger.error(f'Failed to update firm financials')
            db.manual_rollback(db.connection)
            return False
        
        # Finally delete the shareholder
        success = shareholder_repo.delete_shareholder(shareholder_id)
        if not success:
            logger.error(f'Failed to delete shareholder with ID {shareholder_id}')
            db.manual_rollback(db.connection)
            return False
        
        # If everything succeeded, commit the transaction
        db.connection.commit()
        logger.info(f'Successfully processed withdrawal for shareholder {shareholder.name} (ID: {shareholder.id})')
        return True
    
    except Exception as e:
        logger.error(f'Error processing shareholder deletion: {e}', exc_info=True)
        if db.connection and db.connection.closed == 0:
            db.manual_rollback(db.connection)
        return False
    finally:
        if db.connection and db.connection.closed == 0:
            db.connection.autocommit = True