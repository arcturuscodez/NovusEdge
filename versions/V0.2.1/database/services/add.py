from options import o
from utility import is_valid_email
from database.repositories.shareholder import ShareholderRepository

import logging

def handle_add_shareholder(db):
    try:
        parts = o.AddShareholder.split(':')
        if len(parts) != 4:
            print('Invalid number of arguments. Expected 4, got', len(parts))
            return

        name, ownership, investment, email = parts

        if not is_valid_email(email):
            logging.warning('Invalid email address.')
            return
        try:
            ownership = float(ownership)
            investment = float(investment)
        except ValueError:
            logging.error('Ownership and investment must be numeric.')
            return

        repository = ShareholderRepository(db)
        shareholder_id = repository.add_shareholder(name, ownership, investment, email)
        if shareholder_id:
            logging.info(f'Shareholder with name: {name} added successfully.')
        else:
            logging.error(f'Failed to add shareholder with {name}.')
    
    except Exception as e:
        logging.error(f'An error occurred handling the adding of a shareholder to the table: {e}')
        raise