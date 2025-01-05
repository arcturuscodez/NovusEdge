from utility import helpers
from options import o
from database.repositories.shareholder import ShareholderRepository

import logging

logger = logging.getLogger(__name__)

def handle_edit_shareholder(db_conn):
    parts = o.EditShareholder.split(':')
    if len(parts) != 2:
        print(
            "Invalid format for EditShareholder.\n"
            "Expected format: id:key=value\n"
            "Example: 2:investment=1500"
        )
        return
    
    try:
        shareholder_id = int(parts[0])
    except ValueError:
        print("ID must be an integer.")
        return
    
    key_value = parts[1]
    if '=' not in key_value:
        print("Invalid format for update. Expected key=value pair.")
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
            if key == 'email' and not helpers.is_valid_email(value):
                print("Invalid email format.")
                return
    except ValueError:
        print(f"Invalid value type for {key}. Expected {allowed_fields[key].__name__}.")
        return
    
    repository = ShareholderRepository(db_conn)
    try:
        success = repository.edit_shareholder(
            shareholder_id,
            **{key: value}
        )
        if success:
            print(f"Successfully updated Shareholder with ID: {shareholder_id}")
        else:
            print(f"Failed to update Shareholder with ID: {shareholder_id}. Please check the provided details.")
    except Exception as e:
        logger.error(f"Error updating shareholder ID {shareholder_id}: {e}")
        print("An error occurred while updating the shareholder.")