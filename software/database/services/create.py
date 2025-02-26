"""Service module for handling the addition of entities to the database."""
from utility import is_valid_email
from database.repositories.base import GenericRepository
from database.repositories.shareholder import ShareholderRepository
from database.repositories.transaction import TransactionRepository
from database.repositories.portfolio import PortfolioRepository
from database.repositories.firm import FirmRepository

from database.connection import DatabaseConnection

from decimal import Decimal, InvalidOperation

import logging

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

def handle_create_entity(db: DatabaseConnection, table: str, **data):
    """
    Handle the creation of a generic entity in a specified table.

    Args:
        db (DatabaseConnection): The database connection object.
        table (str): The name of the table to create the entity in.
        **data: Keyword arguments representing the entity’s key-value pairs.

    Returns:
        None: Creates the entity and logs/prints the outcome.
    """
    try:
        if not table:
            logger.warning("Table name not provided.")
            print("Error: Table name is required.")
            return

        if not data:
            logger.warning("No data provided for entity creation.")
            print("Error: Entity data is required.")
            return

        logger.debug(f"Creating entity in table '{table}' with data: {data}")
        repository = GenericRepository(db, table)
        entity_id = repository.add(data)

        if entity_id:
            logger.info(f"Entity created in table '{table}' with ID: {entity_id}.")
            print(f"Entity created successfully in '{table}' with ID: {entity_id}.")
        else:
            logger.warning(f"Failed to create entity in table '{table}'.")
            print(f"Error: Failed to create entity in '{table}'.")

    except Exception as e:
        logger.error(f"Error creating entity in table '{table}': {e}")
        print(f"Unexpected error occurred: {e}")
        raise

def handle_create_shareholder(db: DatabaseConnection, name: str, ownership: str, investment: str, email: str):
    """
    Handle the creation of a shareholder in the SHAREHOLDERS table.

    Args:
        db (DatabaseConnection): The database connection object.
        name (str): The shareholder's name.
        ownership (str or float): The percentage ownership (e.g., "10" or 10.0).
        investment (str or float): The investment amount (e.g., "1000" or 1000.0).
        email (str): The shareholder's email address.

    Returns:
        None: Creates the shareholder and logs/prints the outcome.
    """
    try:
        logger.debug(f"Creating shareholder: name={name}, ownership={ownership}, investment={investment}, email={email}")
        if not all([name, ownership, investment, email]):
            logger.warning("All fields (name, ownership, investment, email) must be provided.")
            print("Error: All fields (name, ownership, investment, email) are required.")
            return

        try:
            ownership_value = float(ownership)
            investment_value = float(investment)
        except ValueError:
            logger.error("Ownership and investment must be numeric values.")
            print("Error: Ownership and investment must be numbers.")
            return

        if not (0 < ownership_value <= 100):
            logger.warning(f"Ownership must be between 0 and 100, got {ownership_value}.")
            print(f"Error: Ownership must be between 0 and 100, got {ownership_value}.")
            return

        if investment_value < 0:
            logger.warning(f"Investment must be positive, got {investment_value}.")
            print(f"Error: Investment must be a positive number, got {investment_value}.")
            return

        if not is_valid_email(email):
            logger.warning(f"Invalid email address: {email}.")
            print(f"Error: Invalid email address: {email}.")
            return

        repository = ShareholderRepository(db)
        shareholder_id = repository.add_shareholder(
            name=name,
            ownership=ownership_value,
            investment=investment_value,
            email=email
        )

        if shareholder_id:
            logger.info(f"Shareholder '{name}' created successfully with ID: {shareholder_id}.")
            print(f"Shareholder '{name}' created successfully with ID: {shareholder_id}.")
            firm_repo = FirmRepository(db)
            firm_id = 1  # TODO: Replace with dynamic firm ID
            success = firm_repo.update_firm(firm_id, CASH=investment_value)
            if success:
                logger.info(f"Firm (ID: {firm_id}) CASH updated with investment: {investment_value}.")
            else:
                logger.warning(f"Failed to update firm's CASH for firm ID: {firm_id}.")
                print("Warning: Failed to update firm's cash balance.")
        else:
            logger.warning(f"Failed to create shareholder '{name}'.")
            print(f"Error: Failed to create shareholder '{name}'.")

    except Exception as e:
        logger.error(f"Error creating shareholder: {e}")
        print(f"Unexpected error occurred: {e}")
        raise

def handle_create_transaction(db: DatabaseConnection, ticker: str, shares: str, price_per_share: str, transaction_type: str):
    """
    Handle the creation of a transaction in the TRANSACTIONS table.

    Args:
        db (DatabaseConnection): The database connection object.
        ticker (str): The stock ticker symbol.
        shares (str): Number of shares (converted to Decimal).
        price_per_share (str): Price per share (converted to Decimal).
        transaction_type (str): Type of transaction ('buy' or 'sell').

    Returns:
        None: Creates the transaction and updates portfolio/firm accordingly.
    """
    try:
        logger.debug(f"Creating transaction: ticker={ticker}, shares={shares}, price_per_share={price_per_share}, type={transaction_type}")
        if not all([ticker, shares, price_per_share, transaction_type]):
            logger.warning("All transaction fields (ticker, shares, price_per_share, transaction_type) must be provided.")
            print("Error: All transaction fields are required.")
            return

        try:
            shares_value = Decimal(shares)
            price_per_share_value = Decimal(price_per_share)
            transaction_type_value = transaction_type.lower()
        except (ValueError, InvalidOperation):
            logger.error("Shares and price_per_share must be numeric.")
            print("Error: Shares and price_per_share must be numbers.")
            return

        if transaction_type_value not in ['buy', 'sell']:
            logger.warning(f"Invalid transaction type: {transaction_type_value}. Must be 'buy' or 'sell'.")
            print(f"Error: Transaction type must be 'buy' or 'sell', got '{transaction_type_value}'.")
            return

        portfolio_repo = PortfolioRepository(db)
        transaction_repo = TransactionRepository(db)
        firm_repo = FirmRepository(db)

        if transaction_type_value == 'sell':
            asset = portfolio_repo.get_asset_by_ticker(ticker)
            if not asset or asset.total_shares < shares_value:
                logger.warning(f"Insufficient shares to sell: {shares_value} requested, {asset.total_shares if asset else 0} available.")
                print(f"Error: Insufficient shares to sell ({shares_value} requested, {asset.total_shares if asset else 0} available).")
                return

        if transaction_type_value == 'buy':
            firm_data = firm_repo.get_entity(id=1)  # TODO: Make firm ID dynamic
            if not firm_data or firm_data.cash < shares_value * price_per_share_value:
                logger.warning(f"Insufficient funds to buy: {shares_value * price_per_share_value} required, {firm_data.cash if firm_data else 0} available.")
                print(f"Error: Insufficient funds to buy ({shares_value * price_per_share_value} required, {firm_data.cash if firm_data else 0} available).")
                db.manual_rollback(db.connection)
                return

        transaction_id = transaction_repo.add_transaction(ticker, shares_value, price_per_share_value, transaction_type_value)
        if not transaction_id:
            logger.warning(f"Failed to create transaction for {ticker}.")
            print(f"Error: Failed to create transaction for {ticker}.")
            return

        logger.info(f"Transaction created: {transaction_type_value} {ticker}, {shares_value} shares at {price_per_share_value}, ID: {transaction_id}")
        print(f"Transaction created: {transaction_type_value} {ticker}, {shares_value} shares at {price_per_share_value}, ID: {transaction_id}")

        portfolio_success = portfolio_repo.add_or_update_asset(
            ticker=ticker,
            shares=shares_value if transaction_type_value == 'buy' else -shares_value,
            price_per_share=price_per_share_value,
            transaction_type=transaction_type_value
        )
        if not portfolio_success:
            logger.warning(f"Failed to update portfolio for ticker: {ticker}.")
            print(f"Warning: Failed to update portfolio for {ticker}.")
        else:
            logger.info(f"Portfolio updated successfully for ticker: {ticker}.")

        firm = firm_repo.get_firm(id=1)  # TODO: Make firm ID dynamic
        cash_change = shares_value * price_per_share_value if transaction_type_value == 'sell' else -shares_value * price_per_share_value
        firm_success = firm_repo.update_firm(1, CASH=firm.cash + cash_change)
        if not firm_success:
            logger.warning(f"Failed to update firm cash for transaction: {transaction_id}.")
            print(f"Warning: Failed to update firm cash for transaction {transaction_id}.")
        else:
            logger.info(f"Firm cash updated successfully for transaction: {transaction_id}.")

    except Exception as e:
        logger.error(f"Error creating transaction: {e}")
        print(f"Unexpected error occurred: {e}")
        raise

def handle_create_firm(db: DatabaseConnection, firm_name: str):
    """
    Handle the creation of a new firm with default values.

    Args:
        db (DatabaseConnection): The database connection object.
        firm_name (str): The name of the firm to create.

    Returns:
        None: Creates the firm and logs/prints the outcome.
    """
    try:
        if not firm_name:
            logger.warning("Firm name not provided.")
            print("Error: Firm name is required.")
            return

        if not isinstance(firm_name, str):
            logger.warning(f"Firm name must be a string, got {type(firm_name)}.")
            print(f"Error: Firm name must be a string, got {type(firm_name)}.")
            return

        logger.debug(f"Creating firm: {firm_name}")
        firm_repo = FirmRepository(db)
        firm_id = firm_repo.add_firm(firm_name=firm_name)

        if firm_id:
            logger.info(f"Firm '{firm_name}' created successfully with ID: {firm_id}.")
            print(f"Firm '{firm_name}' created successfully with ID: {firm_id}.")
        else:
            logger.warning(f"Failed to create firm '{firm_name}'.")
            print(f"Error: Failed to create firm '{firm_name}'.")

    except Exception as e:
        logger.error(f"Error creating firm: {e}")
        print(f"Unexpected error occurred: {e}")
        raise

def handle_create_expense(db: DatabaseConnection, firm_id: str, value: str):
    """
    Handle the creation of a new expense for a firm.

    Args:
        db (DatabaseConnection): The database connection object.
        firm_id (str): The ID of the firm (converted to int).
        value (str): The expense value (converted to float).

    Returns:
        None: Creates the expense and logs/prints the outcome.
    """
    try:
        if not all([firm_id, value]):
            logger.warning("Firm ID and expense value must be provided.")
            print("Error: Firm ID and expense value are required.")
            return

        try:
            firm_id_int = int(firm_id)
            value_float = float(value)
        except ValueError:
            logger.error("Firm ID must be an integer and value must be numeric.")
            print("Error: Firm ID must be an integer and value must be a number.")
            return

        logger.debug(f"Creating expense {value_float} for firm ID: {firm_id_int}")
        firm_repo = FirmRepository(db)
        firm = firm_repo.get_firm(firm_id_int)
        if not firm:
            logger.warning(f"Firm with ID {firm_id_int} not found.")
            print(f"Error: Firm with ID {firm_id_int} not found.")
            return

        firm_repo.add_firm_expense(firm_id_int, value_float)
        logger.info(f"Created expense {value_float} for firm with ID: {firm_id_int}")
        print(f"Created expense {value_float} for firm with ID: {firm_id_int}")

    except Exception as e:
        logger.error(f"Error creating expense: {e}")
        print(f"Unexpected error occurred: {e}")
        raise

def handle_create_revenue(db: DatabaseConnection, firm_id: str, value: str):
    """
    Handle the creation of a new revenue for a firm.

    Args:
        db (DatabaseConnection): The database connection object.
        firm_id (str): The ID of the firm (converted to int).
        value (str): The revenue value (converted to float).

    Returns:
        None: Creates the revenue and logs/prints the outcome.
    """
    try:
        if not all([firm_id, value]):
            logger.warning("Firm ID and revenue value must be provided.")
            print("Error: Firm ID and revenue value are required.")
            return

        try:
            firm_id_int = int(firm_id)
            value_float = float(value)
        except ValueError:
            logger.error("Firm ID must be an integer and value must be numeric.")
            print("Error: Firm ID must be an integer and value must be a number.")
            return

        logger.debug(f"Creating revenue {value_float} for firm ID: {firm_id_int}")
        firm_repo = FirmRepository(db)
        firm = firm_repo.get_firm(firm_id_int)
        if not firm:
            logger.warning(f"Firm with ID {firm_id_int} not found.")
            print(f"Error: Firm with ID {firm_id_int} not found.")
            return

        firm_repo.add_firm_revenue(firm_id_int, value_float)
        logger.info(f"Created revenue {value_float} for firm with ID: {firm_id_int}")
        print(f"Created revenue {value_float} for firm with ID: {firm_id_int}")

    except Exception as e:
        logger.error(f"Error creating revenue: {e}")
        print(f"Unexpected error occurred: {e}")
        raise

def handle_create_liability(db: DatabaseConnection, firm_id: str, value: str):
    """
    Handle the creation of a new liability for a firm.

    Args:
        db (DatabaseConnection): The database connection object.
        firm_id (str): The ID of the firm (converted to int).
        value (str): The liability value (converted to float).

    Returns:
        None: Creates the liability and logs/prints the outcome.
    """
    try:
        if not all([firm_id, value]):
            logger.warning("Firm ID and liability value must be provided.")
            print("Error: Firm ID and liability value are required.")
            return

        try:
            firm_id_int = int(firm_id)
            value_float = float(value)
        except ValueError:
            logger.error("Firm ID must be an integer and value must be numeric.")
            print("Error: Firm ID must be an integer and value must be a number.")
            return

        logger.debug(f"Creating liability {value_float} for firm ID: {firm_id_int}")
        firm_repo = FirmRepository(db)
        firm = firm_repo.get_firm(firm_id_int)
        if not firm:
            logger.warning(f"Firm with ID {firm_id_int} not found.")
            print(f"Error: Firm with ID {firm_id_int} not found.")
            return

        firm_repo.add_firm_liability(firm_id_int, value_float)
        logger.info(f"Created liability {value_float} for firm with ID: {firm_id_int}")
        print(f"Created liability {value_float} for firm with ID: {firm_id_int}")

    except Exception as e:
        logger.error(f"Error creating liability: {e}")
        print(f"Unexpected error occurred: {e}")
        raise