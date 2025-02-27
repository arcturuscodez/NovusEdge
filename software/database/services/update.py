"""Service module for handling the updating of an entities fields."""
from datetime import datetime
from utility import is_valid_email
from database.repositories.base import GenericRepository
from database.repositories.shareholder import ShareholderRepository
from database.repositories.transaction import TransactionRepository
from database.repositories.portfolio import PortfolioRepository
from database.repositories.firm import FirmRepository
from database.connection import DatabaseConnection
from icarus.retriever import AssetRetriever

import logging

logger = logging.getLogger(__name__)

def handle_update_entity(db: DatabaseConnection, table: str, entity_id: int, **data) -> bool:
    """
    Handle the updating of a generic entity in a specified table.

    Args:
        db (DatabaseConnection): The database connection object.
        table (str): The name of the table to update.
        entity_id (int): The ID of the entity to update.
        **data: Keyword arguments representing the fields to update (e.g., key=value).

    Returns:
        bool: True if the entity was updated successfully, False otherwise.
    """
    try:
        if not table:
            logger.error("Table name not provided for update")
            return False

        if not isinstance(entity_id, int):
            logger.error(f"Entity ID must be an integer, got {type(entity_id)}")
            return False

        if not data:
            logger.warning("No data provided for entity update")
            return False

        logger.debug(f"Updating entity ID {entity_id} in table '{table}' with data: {data}")
        repository = GenericRepository(db, table)
        success = repository.update(entity_id, **data)

        if success:
            logger.info(f"Entity ID {entity_id} in table '{table}' updated successfully with {data}")
            return True
        else:
            logger.warning(f"Failed to update entity ID {entity_id} in table '{table}' - entity may not exist")
            return False

    except Exception as e:
        logger.error(f"Error updating entity in table '{table}' with ID {entity_id}: {e}", exc_info=True)
        raise

def handle_update_shareholder(db: DatabaseConnection, shareholder_id: int, **data) -> bool:
    """
    Handle the updating of a shareholder's information in the SHAREHOLDERS table.

    Args:
        db (DatabaseConnection): The database connection object.
        shareholder_id (int): The ID of the shareholder to update.
        **data: Keyword arguments representing the fields to update (e.g., name='John').

    Returns:
        bool: True if the shareholder was updated successfully, False otherwise.
    """
    try:
        if not isinstance(shareholder_id, int):
            logger.error(f"Shareholder ID must be an integer, got {type(shareholder_id)}")
            return False

        if not data:
            logger.warning("No data provided for shareholder update")
            return False

        allowed_fields = {
            'name': str,
            'ownership': float,
            'investment': float,
            'email': str,
            'shareholder_status': str
        }

        validated_data = {}
        for key, value in data.items():
            key = key.lower()
            if key not in allowed_fields:
                logger.warning(f"Unknown field for shareholder update: {key}. Allowed fields are: {', '.join(allowed_fields.keys())}")
                return False

            try:
                if allowed_fields[key] == float:
                    validated_data[key] = float(value)
                elif allowed_fields[key] == str:
                    if key == 'email' and not is_valid_email(value):
                        logger.warning(f"Invalid email address: {value}")
                        return False
                    validated_data[key] = value
            except ValueError:
                logger.error(f"Invalid value type for {key}. Expected {allowed_fields[key].__name__}")
                return False

        if 'ownership' in validated_data and not (0 < validated_data['ownership'] <= 100):
            logger.warning(f"Ownership must be between 0 and 100, got {validated_data['ownership']}")
            return False

        logger.debug(f"Updating shareholder ID {shareholder_id} with data: {validated_data}")
        repository = ShareholderRepository(db)
        success = repository.update_shareholder(shareholder_id, **validated_data)

        if success:
            logger.info(f"Shareholder ID {shareholder_id} updated successfully with {validated_data}")
            return True
        else:
            logger.warning(f"Failed to update shareholder ID {shareholder_id} - shareholder may not exist")
            return False

    except Exception as e:
        logger.error(f"Error updating shareholder ID {shareholder_id}: {e}", exc_info=True)
        raise

def handle_update_transaction(db: DatabaseConnection, transaction_id: int, **data) -> bool:
    """
    Handle the updating of a transaction in the TRANSACTIONS table.

    Args:
        db (DatabaseConnection): The database connection object.
        transaction_id (int): The ID of the transaction to update.
        **data: Keyword arguments representing the fields to update (e.g., shares=50).

    Returns:
        bool: True if the transaction was updated successfully, False otherwise.
    """
    try:
        if not isinstance(transaction_id, int):
            logger.error(f"Transaction ID must be an integer, got {type(transaction_id)}")
            return False

        if not data:
            logger.warning("No data provided for transaction update")
            return False

        allowed_fields = {
            'ticker': str,
            'shares': float,
            'price_per_share': float,
            'transaction_type': str
        }

        validated_data = {}
        for key, value in data.items():
            key = key.lower()
            if key not in allowed_fields:
                logger.warning(f"Unknown field for transaction update: {key}. Allowed fields are: {', '.join(allowed_fields.keys())}")
                return False

            try:
                if allowed_fields[key] == float:
                    validated_data[key] = float(value)
                elif allowed_fields[key] == str:
                    if key == 'transaction_type' and value.lower() not in ['buy', 'sell']:
                        logger.warning(f"Invalid transaction type: {value}. Must be 'buy' or 'sell'")
                        return False
                    validated_data[key] = value.lower()
            except ValueError:
                logger.error(f"Invalid value type for {key}. Expected {allowed_fields[key].__name__}")
                return False

        logger.debug(f"Updating transaction ID {transaction_id} with data: {validated_data}")
        repository = TransactionRepository(db)
        success = repository.update_transaction(transaction_id, **validated_data)

        if success:
            logger.info(f"Transaction ID {transaction_id} updated successfully with {validated_data}")
            return True
        else:
            logger.warning(f"Failed to update transaction ID {transaction_id} - transaction may not exist")
            return False

    except Exception as e:
        logger.error(f"Error updating transaction ID {transaction_id}: {e}", exc_info=True)
        raise

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
                logger.info(f"Firm ID {firm_id} total assets updated successfully to {total_assets_value}")
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
            logger.info(f"Last run: {row[0]}, Current time: {now}. Portfolio update already run today. Use --override to override")
            return

        if force_update:
            logger.info("Force update enabled via --override. Proceeding with portfolio update")

        portfolio_repo = PortfolioRepository(db)
        logger.debug("Fetching all portfolio assets")
        assets = portfolio_repo.get_all()

        if not assets:
            logger.info("No assets found in portfolio to update")
            return

        logger.info(f"Updating {len(assets)} portfolio assets with latest data")
        for asset in assets:
            logger.debug(f"Retrieving data for ticker {asset.ticker}")
            retriever = AssetRetriever(ticker=asset.ticker)
            
            latest_price = retriever.get_latest_closing_price()
            if latest_price is not None:
                portfolio_repo.update(asset.id, CURRENT_PRICE=latest_price)
                logger.info(f"Updated {asset.ticker} with latest closing price: {latest_price}")
            else:
                logger.warning(f"Could not retrieve latest closing price for {asset.ticker}")

            dividend_yield = retriever.get_dividend_yield() # Retrieve the dividend yield as a value (e.g., 0.03 for 3%) NOT as a percentage (3%)
            if dividend_yield is not None:
                dividend_yield_percentage = dividend_yield * 100 # Convert to percentage for storage (e.g., 0.03 to 3%) NOT as a decimal (0.03)
                portfolio_repo.update(asset.id, DIVIDEND_YIELD=dividend_yield_percentage)
                logger.info(f"Updated {asset.ticker} with dividend yield: {dividend_yield_percentage:.2f}%")
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
        logger.info("Portfolio updated successfully with latest daily data")

    except Exception as e:
        logger.error(f"Portfolio update failed: {e}", exc_info=True)
        try:
            if db.connection and db.connection.closed == 0:
                db.connection.rollback()
                logger.debug("Rolled back changes due to error")
        except Exception as rollback_error:
            logger.warning(f"Failed to rollback changes: {rollback_error}")
        raise