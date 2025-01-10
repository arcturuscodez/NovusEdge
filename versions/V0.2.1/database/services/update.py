from options import args
from utility import is_valid_email
from database.repositories.generic import GenericRepository
from database.repositories.shareholder import ShareholderRepository

import logging

logger = logging.getLogger(__name__)

def handle_update_entity(db):
    """
    Handle the updating of an entity in a table in the database.

    Args:
        db (object): The database connection object.
    """
    try:
        pass
    except Exception as e:
        logger.error(f'An error occurred handling the updating of an entity in the table: {e}')
        raise
    
def handle_update_shareholder(db):
    """
    Handle the updating of a shareholder's information in the shareholders table.
    
    Args:
        db (object): THe database connection object.
    """    
    try:
        parts = args.EditShareholder.split(':')
        
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
                
        except Exception as e:
            print(f'An unexpected error occurred updating shareholder rows: {e}')
        
    except Exception as e:
        logger.error(f'An error occurred handling the updating of a shareholders values in the table: {e}')
        raise