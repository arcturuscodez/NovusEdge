"""Service module for handling the updating of entities in the database."""
from options import args
from utility import is_valid_email
from database.repositories.generic import GenericRepository
from database.repositories.shareholder import ShareholderRepository
from database.repositories.transaction import TransactionRepository
from database.repositories.portfolio import PortfolioRepository
from database.repositories.firm import FirmRepository

from icarus.retriever import AssetRetriever

import logging

logger = logging.getLogger(__name__)

def handle_update_entity(db) -> bool:
    """
    Handle the updating of an entity in a table in the database.

    Args:
        db (object): The database connection object.
        
    Returns:
        bool: True if the entity was updated successfully, False otherwise.
    """
    try:
        
        if not args.table:
            logger.error('Table name not provided.')
            print('Error: Table name is required for update')
            return
        
        parts = args.update.lower().split(':')
        
        logger.debug('Parts:', parts)
        
        if len(parts) != 2:
            print(
                'Invalid format for update.\n'
                'Expected format: table:id:key=value\n'
                'Example: shareholders:2:investment=1500'
            )
            return
        try:
            entity_id = int(parts[0])
        except ValueError:
            print('Entity ID must be an integer.')
            return
        
        key_value = parts[1]
        if '=' not in key_value:
            print('Invalid format for key=value pair.')
            return
        
        key, value = key_value.split('=', 1)
        key = key.strip().lower()
        value = value.strip()
        
        allowed_fields = {
            # this will somehow need to be either automatically assigned to the correct repository or some other method, maybe use models to dictate the allowed fields
        }
        
        if key not in allowed_fields:
            print(f"Unknown field: {key}. Allowed fields are: {', '.join(allowed_fields.keys())}.")
            return
        
        try:
            if allowed_fields[key] == float:
                value = float(value)
            elif allowed_fields[key] == int:
                value = int(value)
            elif allowed_fields[key] == str:
                if key == 'email' and not is_valid_email(value):
                    print('Invalid email address.')
                    return
                if key == 'transaction_type' and value.lower() not in ['buy', 'sell']:
                    print('Invalid transaction type. Must be either "buy" or "sell".')
                    return
                
        except ValueError:
            print(f"Invalid value type for {key}. Expected {allowed_fields[key].__name__}.")
            return
        
        repository = GenericRepository(db, args.table)
        try:
            success = repository.update(entity_id, **{key: value})
            if success:
                print(f'Entity: {entity_id} updated with {key} and {value} successfully.')
            else:
                print(f'Failed to update entity: {entity_id}.')
                
        except Exception as e:
            print(f'An unexpected error occurred updating entity rows: {e}')
                
    except Exception as e:
        logger.error(f'An error occurred handling the updating of an entity in the table: {e}')
        raise
    
def handle_update_shareholder(db):
    """
    Handle the updating of a shareholder's information in the SHAREHOLDERS table.
    
    Args:
        db (object): The database connection object.
    """    
    try:
        parts = args.UpdateShareholder.split(':')
        
        logger.debug('Parts:', parts)
        
        if len(parts) != 2:
            print(
                'Invalid format for EditShareholder.\n'
                'Expected format: id:key=value\n'
                'Example: 2:investment=1500'
            )
            return
        try:
            shareholder_id = int(parts[0])
        except ValueError:
            print('Shareholder ID must be an integer.')
            return
        
        key_value = parts[1]
        if '=' not in key_value:
            print('Invalid format for key=value pair.')
            return
        
        key, value = key_value.split('=', 1)
        key = key.strip().lower()
        value = value.strip()
        
        allowed_fields = {
            'name': str,
            'ownership': float,
            'investment': float,
            'email': str,
            'shareholder_status': str
        }
        
        if key not in allowed_fields:
            print(f"Unknown field: {key}. Allowed fields are: {', '.join(allowed_fields.keys())}.")
            return
        
        try:
            if allowed_fields[key] == float:
                value = float(value)
            elif allowed_fields[key] == int:
                value = int(value)
            elif allowed_fields[key] == str:
                if key == 'email' and not is_valid_email(value):
                    print('Invalid email address.')
                    return
                
        except ValueError:
            print(f"Invalid value type for {key}. Expected {allowed_fields[key].__name__}.")
            return
        
        repository = ShareholderRepository(db)
        try:
            success = repository.update_shareholder(shareholder_id, **{key: value})
            if success:
                print('Shareholder updated successfully.')
            else:
                print('Failed to update shareholder.')
                return False
                
        except Exception as e:
            print(f'An unexpected error occurred updating shareholder rows: {e}')
        
    except Exception as e:
        logger.error(f'An error occurred handling the updating of a shareholders values in the table: {e}')
        raise
    
def handle_update_transaction(db):
    """
    Handle the updating of a transaction in the TRANSACTIONS table.
    
    Args:
        db (object): The database connection object.
    """
    try:
        parts = args.UpdateTransaction.split(':')

        logger.debug('Parts:', parts)
        
        if len(parts) != 2:
            print(
                'Invalid format for EditTransaction.\n'
                'Expected format: id:key=value\n'
                'Example: 2:shares=50'
            )
            return
        try:
            transaction_id = int(parts[0])
        except ValueError:
            print('Transaction ID must be an integer.')
            return
        
        key_value = parts[1]
        if '=' not in key_value:
            print('Invalid format for key=value pair.')
            return
        
        key, value = key_value.split('=', 1)
        key = key.strip().lower()
        value = value.strip()
        
        allowed_fields = {
            'ticker': str,
            'shares': float,
            'price_per_share': float,
            'transaction_type': str
        }
        
        if key not in allowed_fields:
            print(f"Unknown field: {key}. Allowed fields are: {', '.join(allowed_fields.keys())}.")
            return
        
        try:
            if allowed_fields[key] == float:
                value = float(value)
            elif allowed_fields[key] == int:
                value = int(value)
            elif allowed_fields[key] == str:
                if key == 'transaction_type' and value.lower() not in ['buy', 'sell']:
                    print('Invalid transaction type. Must be either "buy" or "sell".')
                    return
                
        except ValueError:
            print(f"Invalid value type for {key}. Expected {allowed_fields[key].__name__}.")
            return
        
        repository = TransactionRepository(db)
        try:
            success = repository.update_transaction(transaction_id, **{key: value})
            if success:
                print('Transaction updated successfully.')
            else:
                print('Failed to update transaction.')
            
        except Exception as e:
            print(f'An unexpected error occurred updating transaction rows: {e}')
            
    except Exception as e:
        logger.error(f'An error occurred handling the updating of a transaction in the table: {e}')
        raise
    
def handle_update_portfolio(db):
    """ 
    Handle the updating of the fields CURRENT_PRICE and DIVIDEND_YIELD using live data.
    """
    try:
        portfolio_repo = PortfolioRepository(db)
        assets = portfolio_repo.get_all()
        
        for asset in assets:
            retriever = AssetRetriever(ticker=asset.ticker)
            
            # Retrieve Latest Closing Price
            latest_price = retriever.get_latest_closing_price()
            if latest_price is not None:
                portfolio_repo.update(asset.id, CURRENT_PRICE=latest_price)
                logging.info(f'Latest Closing Price for {asset.ticker}: {latest_price}')
            else:
                logger.warning(f'Could not retrieve latest closing price for {asset.ticker}')
                
            dividends = retriever.get_dividend_info()
            if dividends is not None and not dividends.empty:
                latest_dividend = dividends['Dividends'].iloc[-1]
                dividend_yield = (latest_dividend / latest_price) * 100
                portfolio_repo.update(asset.id, DIVIDEND_YIELD=dividend_yield)
                logger.info(f'Dividend Yield for {asset.ticker}: {dividend_yield:.2f}%')
            else:
                logger.info(f'No dividend information available for {asset.ticker}')
                
    except Exception as e:
        logger.error(f'An error occurred updating the portfolio: {e}')