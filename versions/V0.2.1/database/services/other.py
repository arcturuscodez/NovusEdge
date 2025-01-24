"""Service module for handling miscellaneous operations such as printing table data."""
from utility import FormatTableData
from database.repositories.factory import get_repository
from options import args
from datetime import datetime, timedelta

def handle_print_table(db):
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
        
def handle_daily_update(db):
    """Run the update portfolio task once a day."""
    task_name = 'update_portfolio'
    connection, cursor = db
    
    cursor.execute('SELECT last_run FROM tasks WHERE name = %s', (task_name,))
    row = cursor.fetchone()
    now = datetime.now()
    
    if row:
        last_run = row[0]
        if now - last_run < timedelta(days=1):
            print('Update already run today. Skipping.')
            return
        
    from database.services.update import handle_update_portfolio
    handle_update_portfolio(db)
    
    if row:
        cursor.execute('UPDATE task_metadata SET last_run = %s WHERE task_name = %s', (now, task_name))
    else:
        cursor.execute('INSERT INTO task_metadata (task_name, last_run) VALUES (%s, %s)', (task_name, now))
    
    db.commit()
    print('Portfolio updated successfully.')