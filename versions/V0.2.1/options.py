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
    '-t', '--table',
    dest='table',
    type=str,
    metavar='<tablename>',
    help='Print the specified table to the terminal.'
)

database_options.add_argument(
    '-a', '--add',
    dest='add',
    type=str,
    metavar='(-t <table>):key=value',
    help='Add an entity to a table. Requires exact key-value pairs.'
)

database_options.add_argument(
    '-r', '--remove',
    dest='remove',
    type=int,
    metavar='<id> (-t <table>)',
    help='Remove an entity from a table by id.'
)

database_options.add_argument(
    '-e', '--edit',
    dest='edit',
    type=str,
    metavar='<id>:key=value (-t <table>)',
    help='Edit a entity in a table by id.'
)

## Shareholder Options

database_options.add_argument(
    '--as', '--add-shareholder',
    dest='AddShareholder',
    type=str,
    metavar='NAME:OWNERSHIP:INVESTMENT:EMAIL',
    help='Add a shareholder to the SHAREHOLDER table.'
)

database_options.add_argument(
    '--rs', '--remove-shareholder',
    dest='RemoveShareholder',
    type=int,
    metavar='ID',
    help='Remove a shareholder from the SHAREHOLDER table by id.'
)

database_options.add_argument(
    '--us', '--update-shareholder',
    dest='UpdateShareholder',
    type=str,
    metavar='id:key=value',
    help='Edit a shareholder in the SHAREHOLDER table by id.'
)

""" Utility Options """

utility_options = parser.add_argument_group('Utility Options')

utility_options.add_argument(
    '--pt', '--print-table',
    dest='PrintTable',
    type=str,
    metavar='SHAREHOLDER',
    help='Print the specified table to the terminal.'
)

utility_options.add_argument(
    '-v', '--verbose',
    dest='verbose',
    action='store_true',
    default=False,
    help='Enable logging messages.'
)

""" Plotting Options """

plotting_options = parser.add_argument_group('Plotting Options')

args = parser.parse_args()