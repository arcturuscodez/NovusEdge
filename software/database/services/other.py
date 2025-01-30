"""Service module for handling miscellaneous operations such as printing table data."""
from utility import FormatTableData
from database.repositories.factory import get_repository
from database.connection import DatabaseConnection
from options import args
from datetime import datetime, timedelta

import logging

logger = logging.getLogger(__name__)

def handle_print_table(db):
    """
    Print the data from the specified table.

    Args:
        db (object): The database connection object.
    """
    
    table_name = str(args.PrintTable).upper()
    repository = get_repository(table_name, db)
    if repository:
        records = repository.get_all()
        if records:
            column_names = [field for field in records[0].__dataclass_fields__]    
            table_data = [tuple(getattr(record, field) for field in column_names) for record in records]
            FormatTableData(column_names, table_data)
        else:
            print(f"No records found in table '{table_name}'.")
    else:
        print(f'Unknown table name: {table_name} or table not found.')
        
def handle_daily_update(db: DatabaseConnection):
    """
    Run the update portfolio task once a day.
    
    Args:
        db (dict): The database connection parameters.
    """
    connection, cursor = db.get_connection_and_cursor()
    
    task_name = 'update_portfolio'
    try:
        cursor.execute('SELECT last_run FROM task_metadata WHERE task_name = %s', (task_name,))
        row = cursor.fetchone()
        now = datetime.now()
        
        if row and (now - row[0] < timedelta(days=1)):
            logger.info('Live asset data update already run today. Skipping.')
            return
        
        from database.services.update import handle_update_portfolio
        handle_update_portfolio((connection, cursor))
        
        if row:
            cursor.execute('UPDATE task_metadata SET last_run = %s WHERE task_name = %s', (now, task_name))
        else:
            cursor.execute('INSERT INTO task_metadata (task_name, last_run) VALUES (%s, %s)', (task_name, now))
        
        connection.commit()
        logger.warning('Portfolio updated successfully.')
        print('Portfolio updated successfully.')
    
    except Exception as e:
        logger.error(f'Error during daily update: {e}', exc_info=True)
        connection.rollback()
        print(f'Error during daily update: {e}')