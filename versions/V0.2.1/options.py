import sys
import globals
import argparse

parser = argparse.ArgumentParser(
    description='Novus Edge [-option] <command>',
    epilog=f'Software Name: {globals.NAME} | Version: {globals.VERSION}'
)

# Option Groups

""" Database Options """

database_options = parser.add_argument_group('Database Options')

## Shareholder Options

database_options.add_argument(
    '--as', '--add-shareholder',
    dest='AddShareholder',
    type=str,
    metavar='NAME:OWNERSHIP:INVESTMENT:EMAIL',
    help='Add a shareholder to the SHAREHOLDER table.')

""" Utility Options """

utility_options = parser.add_argument_group('Utility Options')

utility_options.add_argument(
    '-t', '--table',
    dest='table',
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