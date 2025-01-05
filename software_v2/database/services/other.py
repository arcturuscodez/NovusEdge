from utility.helpers import FormatTableData
from database.repositories.factory import get_repository
from options import o

def handle_print_table(db_conn):
    table_name = str(o.PrintTable).upper()
    repository = get_repository(table_name, db_conn)
    if repository:
        records = repository.fetch_all()
        if records:
            if table_name == 'SHAREHOLDERS':
                column_names = ['id',
                                'name', 
                                'ownership',
                                'investment',
                                'email',
                                'shareholder_status',
                                'created']
                
            elif table_name == 'TRANSACTIONS':
                column_names = ['id',
                                'firm_id',
                                'ticker',
                                'shares',
                                'price_per_share',
                                'total', 
                                'transaction_type',
                                'timestamp']
                
            elif table_name == 'FIRM':    
                column_names = ['id',
                                'total_value',
                                'total_value_investments',
                                'cash_reserve',
                                'net_profit',
                                'net_loss',
                                'created']
                
            elif table_name =='PORTFOLIO':
                column_names = ['firm_id',
                                'ticker',
                                'shares',
                                'average_purchase_price',
                                'total_invested',
                                'realized_profit_loss',
                                'current_price',
                                'total_value',
                                'unrealized_profit_loss',
                                'dividend_yield_percentage',
                                'dividend_yield_amount',
                                'total_dividends_received',
                                'last_updated']
            else:
                column_names = [field for field in records[0].__dataclass_fields__]
            
            table_data = [tuple(getattr(record, field) for field in column_names) for record in records]
            FormatTableData(column_names, table_data)
        else:
            print(f"No records found in table '{table_name}'.")
    else:
        print(f'Unknown table name: {table_name} or table not found...')