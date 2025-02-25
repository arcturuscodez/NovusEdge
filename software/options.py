import globals
import argparse

parser = argparse.ArgumentParser(
    description='ArgParse [-option] <command>',
    epilog=f'Software Name: {globals.NAME} | Version: {globals.VERSION} | Author: {globals.AUTHOR}'
)

# Option Groups

""" Database Options """

database_options = parser.add_argument_group('Database Options')

## Universal Database Options

database_options.add_argument(
    '-start', '--start_server',
    dest='StartServer',
    action='store_true',
    default=False,
    help='Start the PostgreSQL server.'
)

database_options.add_argument( # Non Functional
    '-stop', '--stop_server',
    dest='StopServer',
    action='store_true',
    default=False,
    help='Stop the PostgreSQL server.'
) 

database_options.add_argument( # Functional
    '-t', '--table',
    dest='table',
    type=str,
    metavar='<tablename>',
    help='Table to interact with. Required for some database operations.'
)

database_options.add_argument( # Untested
    '-a', '--add',
    dest='add',
    type=str,
    metavar='(-t <table>):key=value',
    help='Add an entity to a table. Requires exact key-value pairs.'
)

database_options.add_argument( # Functional
    '-r', '--remove',
    dest='remove',
    type=int,
    metavar='<id> (-t <table>)',
    help='Remove an entity from a table by id.'
)

database_options.add_argument( # Untested
    '-u', '--update',
    dest='update',
    type=str,
    metavar='<id>:key=value (-t <table>)',
    help='Edit a entity in a table by id.'
)

## Table Options

database_options.add_argument( # Functional 
    '--pt', '--print-table',
    dest='PrintTable',
    type=str,
    metavar='SHAREHOLDER',
    help='Print the specified table to the terminal.'
)

## Shareholder Options

database_options.add_argument( # Functional
    '--as', '--add-shareholder',
    dest='AddShareholder',
    type=str,
    metavar='NAME:OWNERSHIP:INVESTMENT:EMAIL',
    help='Add a shareholder to the SHAREHOLDER table.'
)

database_options.add_argument( # Functional
    '--rs', '--remove-shareholder',
    dest='RemoveShareholder',
    type=int,
    metavar='ID',
    help='Remove a shareholder from the SHAREHOLDER table by id.'
)

database_options.add_argument( # Functional
    '--us', '--update-shareholder',
    dest='UpdateShareholder',
    type=str,
    metavar='id:key=value',
    help='Edit a shareholder in the SHAREHOLDER table by id.'
)

## Transaction Options

database_options.add_argument( # Functional
    '--at', '--add-transaction',
    dest='AddTransaction',
    type=str,
    metavar='TICKER:SHARES:PPS:TRANSACTION_TYPE',
    help='Add a transaction to the TRANSACTIONS table.'
)

database_options.add_argument( # Untested/Nonfunctional
    '--rt', '--remove-transaction',
    dest='RemoveTransaction',
    type=int,
    metavar='ID',
    help='Remove a transaction from the TRANSACTIONS table by id.'
)

database_options.add_argument( # Untested/Nonfunctional
    '--ut', '--update-transaction',
    dest='UpdateTransaction',
    type=str,
    metavar='id:key=value',
    help='Edit a transaction in the TRANSACTIONS table by id.'
)

## Firm Options

database_options.add_argument(
    '--af', '--AddFirm',
    dest='AddFirm',
    type=str,
    metavar='<firmname>',
    help='Add a new firm with the specified name. Other fields are set to default values.'
)

database_options.add_argument(
    '--ae', '--add-expense',
    dest='AddExpense',
    type=str,
    metavar='id:value (monthly)',
    help='Add an expense to a firm by id. (Ensure it is monthly).' 
)

database_options.add_argument(
    '--ar', '--add-revenue',
    dest='AddRevenue',
    type=str,
    metavar='id:value (monthly)',
    help='Add a revenue to a firm by id. (Ensure it is monthly).'
)

database_options.add_argument(
    '--al', '--add-liability',
    dest='AddLiability',
    type=str,
    metavar='id:value',
    help='Add a liability to a firm by id.'
)

""" Utility Options """

utility_options = parser.add_argument_group('Utility Options')

utility_options.add_argument( # Functional
    '-v', '--verbose',
    dest='verbose',
    action='store_true',
    default=False,
    help='Enable logging messages.'
)

utility_options.add_argument(
    '-override', '--override',
    dest='override',
    action='store_true',
    default=False,
    help='Override the daily update clause, forcing the update.'
)

""" Plotting Options """

plotting_options = parser.add_argument_group('Plotting Options')

args = parser.parse_args()