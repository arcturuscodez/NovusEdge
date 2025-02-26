"""Service module for handling miscellaneous operations such as printing table data."""
from utility import FormatTableData
from database.repositories.factory import get_repository

import logging

logger = logging.getLogger(__name__)

def handle_print_table(db, table_name):
    """ 
    Print the data from the given table.
    
    Args:
        db (object): THe database connection object.
        table_name (str): The name of the table to print (e.g., 'SHAREHOLDERS').
    
    Returns:
        None: Prints table data to the console or an error message if the table or data is not found.
    """
    try:
        table_name = table_name.upper()
        logger.debug(f'Attempting to print table: {table_name}')
        
        repository = get_repository(table_name, db)
        if not repository:
            logger.error(f'Unknown table name: {table_name} or table repository not found.')
            return
        
        records = repository.get_all()
        if not records:
            logger.info(f'No records found in table: {table_name}')
            return
        
        column_names = [field for field in records[0].__dataclass_fields__]
        logger.debug(f'Column names: {column_names}')
        
        table_data = [tuple(getattr(record, field) for field in column_names) for record in records]
        
        FormatTableData(column_names, table_data)
        logger.info(f'Successfully printed table: {table_name}')
        
    except Exception as e:
        logger.error(f'An unexpected error occurred: {e}')
        raise