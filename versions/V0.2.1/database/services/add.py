from options import args
from utility import is_valid_email
from database.repositories.shareholder import ShareholderRepository

import logging

logger = logging.getLogger(__name__)

def handle_add_entity(db):
    """
    Handle the addition of an entity to a table in the database.

    Args:
        db (object): The database connection object.
    """
    try:
        parts = args.AddEntity.split(':')
        
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
            logger.error('Invalid number of arguments. Expected 4, got', len(parts))
            print('Invalid input format. Please provide the name, ownership, investment, and email separated by colons. name:ownership:investment:email')
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
        else:
            logger.error(f'Failed to add shareholder with name: {name}.')
    
    except Exception as e:
        logger.error(f'An error occurred handling the adding of a shareholder to the table: {e}')
        raise