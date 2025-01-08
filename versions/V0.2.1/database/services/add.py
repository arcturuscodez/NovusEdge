from options import o
from utility import is_valid_email
from database.repositories.shareholder import ShareholderRepository

import logging

def handle_add_shareholder(db):
    try:
        parts = o.AddShareholder.split(':')
        if len(parts) != 4:
            logging.error('Invalid number of arguments. Expected 4, got', len(parts))
            print('Invalid input format. Please provide the name, ownership, investment, and email separated by colons. name:ownership:investment:email')
            return

        name, ownership, investment, email = parts

        if not is_valid_email(email):
            logging.warning('Invalid email address.')
            return
        try:
            ownership = float(ownership)
            investment = float(investment)
            
            if not (0 < ownership <= 100):
                logging.warning('Ownership must be between 0 and 100.')
                return
            
            if investment < 0:
                logging.warning('Investment must be a positive number.')
                return
            
        except ValueError:
            logging.error('Ownership and investment must be numeric.')
            return

        repository = ShareholderRepository(db)
        shareholder_id = repository.add_shareholder(name, ownership, investment, email)
        if shareholder_id:
            logging.info(f'Shareholder with name: {name} added successfully.')
        else:
            logging.error(f'Failed to add shareholder with name: {name}.')
    
    except Exception as e:
        logging.error(f'An error occurred handling the adding of a shareholder to the table: {e}')
        raise