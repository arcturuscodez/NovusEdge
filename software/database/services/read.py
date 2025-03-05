"""Service module for handling miscellaneous operations such as printing table data."""
from utility import format_table_data, format_entity_data
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
        
        format_table_data(column_names, table_data)
        logger.debug(f'Successfully printed table: {table_name}')
        
    except Exception as e:
        logger.error(f'An unexpected error occurred: {e}')
        raise
    
def handle_get_by_id(db, table_name: str, entity_id: int):
    """ 
    Get a single entity by its ID.
    
    Args:
        db: Database connection object
        table_name (str): Name of the table to search
        entity_id (int): ID of the entity to retrieve
        
    Returns:
        Optional[BaseModel]: The entity object if found, None otherwise
    """
    try:
        repository = get_repository(table_name, db)
        format_entity_data(repository.get_entity(id=entity_id))
    except Exception as e:
        logger.error(f'An unexpected error occurred retrieving by ID: {e}')
        raise
    
def handle_get_filtered(db, table_name: str, filters: dict, limit: int = None):
    """ 
    Get entities matching specified filters.
    
    Args:
        db: Database connection object
        table_name (str): Name of the table to search
        filters (dict): Dictionary of field names and values to filter by
        limit (int): Maximum number of records to return
    
    Returns:
        List[BaseModel]: List of entity objects matching the filters
    """
    try:
        repository = get_repository(table_name, db)
        return repository.get_all(filters=filters, limit=limit)
    except Exception as e:
        logger.error(f'An unexpected error occurred retrieving by filters: {e}')
        raise