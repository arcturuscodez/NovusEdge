from utility import FormatTableData
from database.repositories.factory import get_repository
from options import args

def handle_print_table(db_conn):
    table_name = str(args.PrintTable).upper()
    repository = get_repository(table_name, db_conn)
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