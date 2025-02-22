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
            if table_name == 'SHAREHOLDERS':
                column_names = ['id',
                                'name', 
                                'ownership',
                                'investment',
                                'email',
                                'shareholder_status',
                                'created_at']

            else:
                column_names = [field for field in records[0].__dataclass_fields__]
                
            table_data = [tuple(getattr(record, field) for field in column_names) for record in records]
            FormatTableData(column_names, table_data)
        else:
            print(f"No records found in table '{table_name}'.")
    else:
        print(f'Unknown table name: {table_name} or table not found.')
        
def handle_daily_update(db_params):
    """
    Run the update portfolio task once a day.
    
    Args:
        db (dict): The database connection parameters.
    """
    with DatabaseConnection(**db_params) as (connection, cursor):
        task_name = 'update_portfolio'
        try:
            cursor.execute('SELECT last_run FROM task_metadata WHERE task_name = %s', (task_name,))
            row = cursor.fetchone()
            now = datetime.now()
            
            if row:
                last_run = row[0]
                if now - last_run < timedelta(days=1):
                    logger.info('Update already run today. Skipping.')
                    print('Update already run today. Skipping.')
                    return
            
            from database.services.update import handle_update_portfolio
            handle_update_portfolio((connection, cursor))
            
            if row:
                cursor.execute('UPDATE task_metadata SET last_run = %s WHERE task_name = %s', (now, task_name))
            else:
                cursor.execute('INSERT INTO task_metadata (task_name, last_run) VALUES (%s, %s)', (task_name, now))
            
            connection.commit()
            logger.info('Portfolio updated successfully.')
            print('Portfolio updated successfully.')
        
        except Exception as e:
            logger.error(f'Error during daily update: {e}', exc_info=True)
            connection.rollback()
            print(f'Error during daily update: {e}')