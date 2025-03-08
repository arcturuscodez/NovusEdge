"""Service module for handling the deletion of an entity from a table."""
from psycopg2.errors import UndefinedTable
from database.repositories.base import BaseRepository
from database.repositories.shareholder import ShareholderRepository
from database.repositories.transaction import TransactionRepository
from database.repositories.firm import FirmRepository
from database.repositories.portfolio import PortfolioRepository
from database.connection import DatabaseConnection

from icarus.analysis.finance import BearhouseCapitalFeeCalculator

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
            return handle_delete_shareholder_v2(db, entity_id)
        
        logger.debug(f"Attempting to delete entity ID {entity_id} from table '{table}'")
        repository = BaseRepository.for_table(db, table)
        result = repository.delete(entity_id)

        if result:
            logger.info(f"Entity with ID {entity_id} from table '{table}' deleted successfully")
            return True
        else:
            logger.warning(f"Failed to delete entity with ID {entity_id} from table '{table}' - entity may not exist")
            return False

    except UndefinedTable as e:
        logger.error(f"Table '{table}' not found: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error deleting entity from table '{table}' with ID {entity_id}: {e}", exc_info=True)
        raise
            
def handle_delete_shareholder_v2(db: DatabaseConnection, shareholder_id: int) -> bool:
    """Handle shareholder deletion with interactive terminal confirmations.
    
    Args:
        db (DatabaseConnection): Database connection object
        shareholder_id (int): ID of the shareholder to delete
        
    Returns:
        bool: True if shareholder was successfully deleted, False otherwise
    """
    try:
        shareholder_repo = ShareholderRepository(db)
        shareholder = shareholder_repo.get_entity(id=shareholder_id)
        if not shareholder:
            logger.warning(f'Shareholder with ID {shareholder_id} not found')
            return False
        
        logger.debug(f'Processing withdrawal for shareholder {shareholder.name} (ID: {shareholder.id})')
        
        print(f"\n===== SHAREHOLDER WITHDRAWAL PROCESS =====")
        print(f"Name: {shareholder.name}")
        print(f"Ownership: {shareholder.ownership}%")
        print(f"Investment: ${shareholder.investment}")
        print(f"======================================")

        confirmation = input("\nAre you sure you want to proceed with the withdrawal? (y/n): ")
        if confirmation.lower() not in ['yes', 'y']:
            print("Withdrawal process cancelled.")
            return False
        
        # Calculate total firm value and shareholder's portion
        firm_repo = FirmRepository(db)
        firm = firm_repo.get_entity(id=1) # TODO: Make firm ID dynamic
        total_firm_value = Decimal(str(firm.cash)) + Decimal(str(firm.assets))
        shareholder_value = total_firm_value * (Decimal(str(shareholder.ownership)) / Decimal('100'))
        
        print(f"\n=== WITHDRAWAL CALCULATION ===")
        print(f"Total firm value: ${total_firm_value}")
        print(f"Shareholder entitled value: ${shareholder_value}")
        print(f"Initial investment: ${shareholder.investment}")
        
        # Determine profit/loss
        is_profit = shareholder_value > Decimal(str(shareholder.investment))
        if is_profit:
            profit = shareholder_value - Decimal(str(shareholder.investment))
            print(f"Profit: ${profit} (will be subject to exit fee)")
            logger.info(f'Profit: ${profit} (will be subject to exit fee)')
        else:
            loss = Decimal(str(shareholder.investment)) - shareholder_value
            print(f"Loss: ${loss} (no exit fee)")
            logger.info(f'Loss: ${loss} (no exit fee)')
            
        # Ask user to confirm calculations
        confirmation = input("\nAre the calculations correct? (y/n): ")
        if confirmation.lower() not in ['yes', 'y']:
            logger.warning("Withdrawal process cancelled.")
            db.manual_rollback(db.connection)
            return False
        
        # Prioritize cash withdrawal over asset liquidation
        cash_withdrawal = min(Decimal(str(firm.cash)), shareholder_value)
        remaining_value = shareholder_value - cash_withdrawal
        
        print(f"\n=== WITHDRAWAL PLAN ===")
        print(f"Cash withdrawal: ${cash_withdrawal}")
        
        # Initialize variables used later
        total_liquidation_value = Decimal('0')
        total_asset_value_reduction = Decimal('0')
        transaction_repo = TransactionRepository(db)
        
        if remaining_value > 0:
            logger.warning(f"Remaining value: ${remaining_value} will be liquidated from assets")
            
            # Get confirmation for asset liquidation
            confirmation = input("\nProceed with asset liquidation? (y/n): ")
            if confirmation.lower() not in ['yes', 'y']:
                logger.warning("Asset liquidation cancelled.")
                db.manual_rollback(db.connection)
                return False
    
            portfolio_repo = PortfolioRepository(db)
            assets = portfolio_repo.get_all()
            
            print(f"\n=== ASSET LIQUIDATION ===")
            
            total_assets_value = sum(
                Decimal(str(asset.total_shares)) * Decimal(str(asset.current_price))
                for asset in assets if asset.current_price and asset.total_shares > 0 
            )
            
            liquidation_plans = []
            for asset in assets:
                if not asset.current_price or asset.total_shares == 0:
                    continue
                
                # Calculate proportion of this asset to liquidate
                asset_value = Decimal(str(asset.total_shares)) * Decimal(str(asset.current_price))
                liquidation_proportion = remaining_value / total_assets_value
                
                # Calculate exact shares and rounded shares to liquidate
                exact_shares_to_sell = Decimal(str(asset.total_shares)) * liquidation_proportion
                # Round to 2 decimal places for display
                display_exact = exact_shares_to_sell.quantize(Decimal('0.01'))
                
                # Round to whole shares
                whole_shares_to_sell = exact_shares_to_sell.quantize(Decimal('1'), rounding='ROUND_UP')
                whole_shares_to_sell = min(whole_shares_to_sell, Decimal(str(asset.total_shares)))
                
                if whole_shares_to_sell > 0:
                    liquidation_value = whole_shares_to_sell * Decimal(str(asset.current_price))
                    liquidation_plans.append({
                        'ticker': asset.ticker,
                        'exact_shares': exact_shares_to_sell,
                        'whole_shares': whole_shares_to_sell,
                        'price': asset.current_price, 
                        'value': liquidation_value
                    })
                    print(f"  {asset.ticker}: {display_exact} shares (rounded to {whole_shares_to_sell}) = ${liquidation_value}")
                    
            total_liquidation_value = sum(plan['value'] for plan in liquidation_plans)
            total_asset_value_reduction = total_liquidation_value
            
            # Get final confirmation for the specific liquidation plan
            confirmation = input("\nConfirm this liquidation plan? (y/n): ")
            if confirmation.lower() not in ['yes', 'y']:
                print("Withdrawal cancelled.")
                db.manual_rollback(db.connection)
                return False
    
        print("\n=== WITHDRAWAL SUMMARY ===")
        print(f"Shareholder: {shareholder.name}")
        print(f"Cash withdrawn: ${cash_withdrawal}")
        if remaining_value > 0:
            print(f"Assets liquidated: ${total_liquidation_value}")
        print(f"Total withdrawn: ${cash_withdrawal + total_liquidation_value}")
        
        # Apply management fee if profit
        management_fee = Decimal('0')
        if is_profit:
            # Apply management fee, if profit
            fee_calculator = BearhouseCapitalFeeCalculator()
            management_fee = fee_calculator.calculate_management_fee(profit)
            print(f"Management fee: ${management_fee}")
            value_shareholder_receives = profit - management_fee
            print(f"Net profit: ${value_shareholder_receives}")

            # Adjust cash withdrawal to account for management fee
            # The fee stays in the firm's cash
            cash_withdrawal = cash_withdrawal - management_fee
            print(f"Final cash withdrawal (after fee): ${cash_withdrawal}")
            
        # Update firm cash and assets
        updated_cash = Decimal(str(firm.cash)) - cash_withdrawal
        updated_assets = Decimal(str(firm.assets)) - total_asset_value_reduction
        
        # Log the changes
        logger.info(f"Updating firm: Cash from ${firm.cash} to ${updated_cash}")
        logger.info(f"Updating firm: Assets from ${firm.assets} to ${updated_assets}")
        
        firm_success = firm_repo.update_firm(1, CASH=updated_cash, ASSETS=updated_assets)
        if not firm_success:
            logger.error(f'Failed to update firm financials')
            db.manual_rollback(db.connection)
            return False
            
        # Execute transactions for asset liquidation
        if remaining_value > 0:
            portfolio_repo = PortfolioRepository(db)
            for plan in liquidation_plans:
                # Create a transaction record for the liquidation
                transaction_id = transaction_repo.create_transaction(
                    ticker=plan['ticker'],
                    shares=plan['whole_shares'],
                    price_per_share=plan['price'],
                    transaction_type='sell'
                )
                
                if not transaction_id:
                    logger.error(f"Failed to create transaction record for {plan['ticker']}")
                    db.manual_rollback(db.connection)
                    return False
                
                # Update portfolio to reflect the sold shares
                success = portfolio_repo.create_or_update_asset(
                    ticker=plan['ticker'],
                    shares=-plan['whole_shares'],  # Negative for selling
                    price_per_share=plan['price'],
                    transaction_type='sell'
                )
                
                if not success:
                    logger.error(f"Failed to update portfolio for {plan['ticker']}")
                    db.manual_rollback(db.connection)
                    return False
                
        final_confirmation = input("\nComplete shareholder withdrawal? THIS IS IRREVERSIBLE (y/n): ")
        if final_confirmation.lower() not in ['yes', 'y']:
            print("Withdrawal cancelled.")
            db.manual_rollback(db.connection)
            return False
        
        # Finally, delete the shareholder
        success = shareholder_repo.delete_shareholder(shareholder_id)
        if not success:
            logger.error(f"Failed to delete shareholder with ID {shareholder_id}")
            db.manual_rollback(db.connection)
            return False
            
        db.connection.commit()
        print(f"\nSuccessfully processed withdrawal for shareholder {shareholder.name}")
        logger.info("Withdrawal completed successfully.")
        return True
        
    except Exception as e:
        logger.error(f"Error in shareholder withdrawal process: {e}", exc_info=True)
        if db.connection and db.connection.closed == 0:
            db.manual_rollback(db.connection)
        print(f"\nError occurred: {e}")
        return False
