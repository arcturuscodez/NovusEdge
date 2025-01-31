"""Service module for handling the addition of entities to the database."""
from options import args
from utility import is_valid_email
from database.repositories.generic import GenericRepository
from database.repositories.shareholder import ShareholderRepository
from database.repositories.transaction import TransactionRepository
from database.repositories.portfolio import PortfolioRepository
from database.repositories.firm import FirmRepository

from decimal import Decimal, InvalidOperation

import logging

logger = logging.getLogger(__name__)

def handle_add_entity(db):
    """
    Handle the addition of an entity to a table in the database.

    Args:
        db (object): The database connection object.
    """
    try:
        if not args.table:
            logger.warning('Warning: Table name not provided.')
            return
        
        if not args.add:
            logger.warning('Entity not provided.')
            return
        
        key_values = args.add.split(':')
        data = {}
        for kv in key_values:
            key, value = kv.split('=')
            data[key] = value
        
        repository = GenericRepository(db, args.table)
        entity_id = repository.add(data)
        if entity_id:
            logger.info(f'Entity added to table: {args.table} with id: {entity_id}.')
            print(f'Entity added successfully with id: {entity_id}.')
        else:
            logger.warning(f'Failed to add entity to table: {args.table}.')
                
    except Exception as e:
        logger.error(f'An error occurred handling the adding of an entity to the table: {e}')
        raise
        
def handle_add_shareholder(db):
    """
    Handle the addition of a shareholder to the shareholders table.

    Args:
        db (object): The database connection object.
    """
    try:
        parts = args.AddShareholder.split(':')
        logger.debug('Parts:', parts)
        if len(parts) != 4:
            logger.warning('Invalid input format. Please provide the name, ownership, investment, and email separated by colons. name:ownership:investment:email')
            return

        name, ownership, investment, email = parts

        if not is_valid_email(email):
            logger.warning('Invalid email address.')
            return
        try:
            ownership = float(ownership)
            investment = float(investment)
            
            if not (0 < ownership <= 100):
                logger.warning('Ownership must be between 0 and 100.')
                return
            
            if investment < 0:
                logger.warning('Investment must be a positive number.')
                return
            
        except ValueError:
            logger.error('Ownership and investment must be numeric.')
            return

        repository = ShareholderRepository(db)
        shareholder_id = repository.add_shareholder(name, ownership, investment, email)
        if shareholder_id:
            logger.info(f'Shareholder with name: {name} added successfully.')
            print(f'Shareholder with name: {name} added successfully as id: {shareholder_id}.')
            
            # Update the FIRM table with the new shareholder's investment
            firm_repo = FirmRepository(db)
            firm_id = 1 # Replace with appropriate firm ID
            success = firm_repo.update_firm(firm_id, CASH=investment)
            if success:
                logger.info(f'Firm\'s CASH updated successfully with investment: {investment}.')
            else:
                logger.warning('Failed to update firm\'s CASH.')
            
        else:
            logger.warning(f'Failed to add shareholder with name: {name}.')
    
    except Exception as e:
        logger.warning(f'An error occurred handling the adding of a shareholder to the table: {e}')
        raise
    
def handle_add_transaction(db):
    """ 
    Handle the addition of a transaction to the transactions table.
    
    Args:
        db (object): The database connection object.
    """
    try:
        def parse_transaction_args(args):
            try:
                parts = args.AddTransaction.split(':')
                if len(parts) != 4:
                    raise ValueError('Invalid format. Expected ticker:shares:price_per_share:transaction_type.')
                ticker, shares, price_per_share, transaction_type = parts
                return ticker, Decimal(shares), Decimal(price_per_share), transaction_type.lower()
            except (ValueError, InvalidOperation):
                raise ValueError('Invalid input values. Ensure shares and price_per_share are numbers.')
        
        try:
            ticker, shares, price_per_share, transaction_type = parse_transaction_args(args)
        except ValueError as e:
            logger.error(e)
            return
        
        if transaction_type not in ['buy', 'sell']:
            logger.warning('Transaction type must be either "buy" or "sell".')
            return
        
        portfolio_repo = PortfolioRepository(db)
        transaction_repo = TransactionRepository(db)
        firm_repo = FirmRepository(db)
        
        if transaction_type == 'sell':
            asset = portfolio_repo.get_asset_by_ticker(ticker)
            if not asset or asset.total_shares < shares:
                logger.warning(f'Insufficient shares to sell: {shares} requested, {asset.total_shares if asset else 0} available.')
                return
            
        # Add transaction
        transaction_id = transaction_repo.add_transaction(ticker, shares, price_per_share, transaction_type)
        if not transaction_id:
            logger.warning(f'Failed to add transaction for {ticker}.')
            return
        
        print(f'Transaction added: {transaction_type} {ticker}, {shares} shares at {price_per_share}, ID: {transaction_id}')
        
        # Update portfolio
        portfolio_success = portfolio_repo.add_or_update_asset(
            ticker=ticker,
            shares=shares if transaction_type == 'buy' else -shares,
            price_per_share=price_per_share,
            transaction_type=transaction_type
        )
        if not portfolio_success:
            logger.warning(f'Failed to update portfolio for ticker: {ticker}.')
        else:
            logger.info(f'Portfolio updated successfully for ticker: {ticker}.')
            
        # Update firm
        
        firm = firm_repo.get_firm(id=1)
        firm_success = firm_repo.update_firm(
            1,
            CASH=firm.cash + (shares * price_per_share if transaction_type == 'sell' else -shares * price_per_share)
            )
        if not firm_success:
            logger.warning(f'Failed to update firm for transaction: {transaction_id}.')
        else:
            logger.info(f'Firm updated successfully for transaction: {transaction_id}.')
            
    except Exception as e:
        logger.warning(f'Error handling transaction: {e}')
        raise
    
def handle_add_firm(db):
    """
    Handle the addition of a new firm with default values.
    
    The firm name is provided via the '--af <firmname>' command-line option.
    All other fields in the FIRM table are set to their default values.
    
    Args:
        db: Database connection/session.
    """
    try:
        firm_name = args.AddFirm
        if not firm_name:
            logger.warning('Firm name not provided. Use the --af <firmname> option.')
            return
        
        if not str(firm_name):
            logger.warning('Firm name must be a string.')
            return

        firm_repo = FirmRepository(db)

        firm_id = firm_repo.add_firm(firm_name=firm_name)

        if firm_id:
            logger.info(f'Firm "{firm_name}" added successfully with ID: {firm_id}.')
            print(f'Firm "{firm_name}" added successfully with ID: {firm_id}.')
        else:
            logger.warning('Failed to add firm.')

    except Exception as e:
        logger.error(f'An unexpected error occurred while adding the firm: {e}')
        print('An unexpected error occurred while adding the firm.')
        raise

def handle_add_expense(db):
    """
    Handle the addition of a new expense into the firm's expenses column.
    """
    try:
        pass # add an expense to the column
        # subtract this value from the profit_loss column in the firm table (profit_loss is monthly or quarterly)
    except Exception as e:
        logger.error(f'An unexpected error occurred while adding the expense: {e}')
        raise
    
def handle_add_liability(db):
    """
    Handle the addition of a new liability into the firm's liabilities column.
    """
    try:
        pass
    except Exception as e:
        logger.error(f'An unexpected error occurred while adding the liability: {e}')
        raise