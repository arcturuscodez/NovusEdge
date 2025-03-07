"""Service module for handling the updating of an entities fields."""
from datetime import datetime
from utility import is_valid_email
from database.repositories.base import BaseRepository
from database.repositories.shareholder import ShareholderRepository
from database.repositories.transaction import TransactionRepository
from database.repositories.portfolio import PortfolioRepository
from database.repositories.firm import FirmRepository
from database.connection import DatabaseConnection
from icarus.retriever import AssetRetriever

import logging

logger = logging.getLogger(__name__)

def handle_update_entity_by_id(db: DatabaseConnection, table_name: str, entity_id: int, **data) -> bool:
    """
    Master function that handles updating any entity and delegates to specific handlers when needed.
    
    Args:
        db: Database connection object.
        table_name: Table name containing the entity to update.
        entity_id: ID of the entity to update.
        **data: Keyword arguments containing the fields to update.
    Returns:
        bool: True if the entity was updated successfully, False otherwise.
    """
    try:
        logger.debug(f'Updating entity with ID {entity_id} in table {table_name}: {data}')

        for key, value in data.items():
            if value == '':
                logger.error(f'Field {key} cannot be empty.')
                return False

        if table_name.lower() == 'shareholders' and any(field in ['name', 'investment', 'email'] for field in data):
            return handle_update_shareholder(db, entity_id, **data)
        elif table_name.lower() == 'transactions' and any(field in ['shares', 'price_per_share', 'transaction_type'] for field in data):
            return handle_update_transaction(db, entity_id, **data)

        repository = BaseRepository.for_table(db, table_name)
        success = repository.update(entity_id, **data)
        
        if success:
            logger.info(f"Successfully updated {table_name} with ID {entity_id}")
        else:
            logger.warning(f"Failed to update {table_name} with ID {entity_id}")
            
        return success
            
    except Exception as e:
        logger.error(f"Error updating entity: {e}", exc_info=True)
        return False
    
def handle_update_shareholder(db: DatabaseConnection, shareholder_id: int, **data) -> bool:
    """
    Handle special cases for updating shareholder entities.

    Args:
        db (DatabaseConnection): The database connection object.
        shareholder_id (int): The ID of the shareholder to update.
        **data: Keyword arguments containing the fields to update.

    Returns:
        bool: True if the shareholder was updated successfully, False otherwise.
    """
    try:
        logger.debug(f'Updating shareholder with ID {shareholder_id}: {data}')

        if 'email' in data and not is_valid_email(data['email']):
            logger.error(f"Invalid email address: {data['email']}")
            return False
        
        repository = ShareholderRepository(db)
        success = repository.update(shareholder_id, **data)
        if success:
            logger.info(f"Successfully updated shareholder with ID {shareholder_id} with data: {data}")
            return True
        else:
            logger.warning(f"Failed to update shareholder with ID {shareholder_id}")
            return False
    
    except Exception as e:
        logger.error(f"Error updating shareholder: {e}", exc_info=True)
        return False

    
def handle_update_transaction(db: DatabaseConnection, transaction_id: int, **data) -> bool:
    """TODO: Implement a redesigned function."""

async def handle_update_portfolio_assets_data(db: DatabaseConnection):
    """
    Asynchronously update the ASSETS field in the FIRM table using the PORTFOLIO TOTAL_VALUE column.

    Args:
        db (DatabaseConnection): The database connection object.

    Returns:
        None: Updates the firm’s assets and logs the outcome.
    """
    try:
        logger.debug("Starting portfolio assets update")
        portfolio_repo = PortfolioRepository(db)
        firm_repo = FirmRepository(db)

        logger.debug("Fetching all portfolio assets")
        assets = portfolio_repo.get_all()
        total_assets_value = sum(asset.total_value for asset in assets if asset.total_value is not None)
        logger.debug(f"Calculated total assets value: {total_assets_value}")

        firm_id = 1  # TODO: Make firm ID dynamic
        logger.debug(f"Retrieving firm with ID {firm_id}")
        firm = firm_repo.get_firm(firm_id)
        if firm:
            logger.debug(f"Updating firm ID {firm_id} assets to {total_assets_value}")
            success = firm_repo.update_firm(firm_id, assets=total_assets_value)
            if success:
                logger.debug(f"Firm ID {firm_id} total assets updated successfully to {total_assets_value}")
            else:
                logger.warning(f"Failed to update firm assets for ID {firm_id}")
        else:
            logger.warning(f"Firm with ID {firm_id} not found")

    except Exception as e:
        logger.error(f"Error updating firm assets: {e}", exc_info=True)
        raise

def handle_daily_update(db: DatabaseConnection, force_update: bool = False):
    """
    Run the portfolio update task once per day, using the latest stock price data, unless forced to override.

    This function checks the TASK_METADATA table to see if the update has already run today.
    If it has, it skips the update unless force_update is True.

    Args:
        db (DatabaseConnection): The active database connection object.
        force_update (bool, optional): If True, ignores the TASK_METADATA check and forces the update. Defaults to False.

    Returns:
        None: Updates the portfolio and logs the outcome.
    """
    task_name = 'update_portfolio'

    if not hasattr(db, 'connection') or db.connection is None or db.connection.closed != 0:
        logger.error("Daily update aborted: Database connection not available")
        return

    try:
        logger.debug(f"Checking last run time for task '{task_name}'")
        db.cursor.execute('SELECT last_run FROM task_metadata WHERE task_name = %s', (task_name,))
        row = db.cursor.fetchone()
        now = datetime.now()

        if not force_update and row and row[0].date() == now.date():
            logger.debug(f"Last run: {row[0]}, Current time: {now}. Portfolio update already run today. Use --override to override")
            return

        if force_update:
            logger.info("Force update enabled via --override. Proceeding with portfolio update")

        portfolio_repo = PortfolioRepository(db)
        logger.debug("Fetching all portfolio assets")
        assets = portfolio_repo.get_all()

        if not assets:
            logger.debug("No assets found in portfolio to update")
            return

        logger.debug(f"Updating {len(assets)} portfolio assets with latest data")
        for asset in assets:
            logger.debug(f"Retrieving data for ticker {asset.ticker}")
            retriever = AssetRetriever(ticker=asset.ticker)
            
            latest_price = retriever.get_latest_closing_price()
            if latest_price is not None:
                portfolio_repo.update(asset.id, CURRENT_PRICE=latest_price)
                logger.debug(f"Updated {asset.ticker} with latest closing price: {latest_price}")
            else:
                logger.warning(f"Could not retrieve latest closing price for {asset.ticker}")

            dividend_yield = retriever.get_dividend_yield() # Retrieve the dividend yield as a value (e.g., 0.03 for 3%) NOT as a percentage (3%)
            if dividend_yield is not None:
                dividend_yield_percentage = dividend_yield * 100 # Convert to percentage for storage (e.g., 0.03 to 3%) NOT as a decimal (0.03)
                portfolio_repo.update(asset.id, DIVIDEND_YIELD=dividend_yield_percentage)
                logger.debug(f"Updated {asset.ticker} with dividend yield: {dividend_yield_percentage:.2f}%")
            else:
                logger.warning(f"Could not retrieve dividend yield for {asset.ticker}")
            
        # Below should use new Task repo methods.
        
        if row:
            logger.debug(f"Updating TASK_METADATA for '{task_name}' with last_run: {now}")
            db.cursor.execute('UPDATE task_metadata SET last_run = %s WHERE task_name = %s', (now, task_name))
        else:
            logger.debug(f"Inserting TASK_METADATA for '{task_name}' with last_run: {now}")
            db.cursor.execute('INSERT INTO task_metadata (task_name, last_run) VALUES (%s, %s)', (task_name, now))

        db.connection.commit()
        logger.info("Portfolio update completed successfully")

    except Exception as e:
        logger.error(f"Portfolio update failed: {e}", exc_info=True)
        try:
            if db.connection and db.connection.closed == 0:
                db.connection.rollback()
                logger.debug("Rolled back changes due to error")
        except Exception as rollback_error:
            logger.warning(f"Failed to rollback changes: {rollback_error}")
        raise