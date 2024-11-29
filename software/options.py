import sys
import globals as g
from optparse import OptionParser, OptionGroup

o = OptionParser(usage='main [-option] <command>',
    version=f'Program Name: {g.NAME}, Version: {g.VERSION}')

UTILITY_GROUP = OptionGroup(o, "Utility Options", "Options for various software systems.")
SHAREHOLDER_DB_GROUP = OptionGroup(o, "Shareholder Database Options", "Options for the use of the SHAREHOLDER table.")
FIRM_DB_GROUP = OptionGroup(o, "Firm Database Options", "Options for the use of the FIRM table.")
TRANSACTION_DB_GROUP = OptionGroup(o, "Transaction Database Options", "Options for the use of the TRANSACTION table.")
PORTFOLIO_DB_GROUP = OptionGroup(o, "Portfolio Options", "Options for the use of the PORTFOLIO table.")

UTILITY_GROUP.add_option('--ST', '--showtable',
    dest='PrintTable',
    type=str,
    default=None,
    metavar='SHAREHOLDER',
    help='Print a table directly to the terminal.'
)

UTILITY_GROUP.add_option('--T', '--Truncate',
    dest='Truncate',
    type=str,
    default=None,
    metavar='SHAREHOLDERS, FIRM',
    help='Truncate all (or a given) table data perserving formatting, triggers, functions.')

UTILITY_GROUP.add_option('--cs', '--checkstock',
    dest='CheckStock',
    action='store_true',
    default=False,
    help='Check if a stock exists in YF.')

SHAREHOLDER_DB_GROUP.add_option('--AS', '--Add',
    dest='AddShareholder',
    type=str,
    default=None,
    metavar='John:75:1000:John@outlook.com',
    help='Add a shareholder with the command NAME:OWNERSHIP:SHARES:EMAIL'
)

SHAREHOLDER_DB_GROUP.add_option('--RS', '--Remove',
    dest='RemoveShareholder',
    type=int,
    default=None,
    metavar='ID',
    help='Remove a shareholder by their ID'
)

SHAREHOLDER_DB_GROUP.add_option('--ES', '--Editshareholder',
    dest='EditShareholder',
    type=str,
    default=None,
    metavar='"<ID> key=value"',
    help='Edit a shareholders information or values. Ensure you are using quotation marks.'
)

FIRM_DB_GROUP.add_option('--init', '--initializefirm',
    dest='InitializeFirmTable',
    action='store_true',
    default=False,
    help='Initialize the firm table.')

TRANSACTION_DB_GROUP.add_option('--buy', '--buystock',
    dest='BuyStock',
    type=str,
    default=None,
    metavar='KO:1000:50',
    help='Buy a stock TICKER:SHARES:PPS'
)

TRANSACTION_DB_GROUP.add_option('--sell', '--sellstock',
    dest='SellStock',
    type=str,
    default=None,
    metavar='KO:1000:50',
    help='Sell a stock TICKER:SHARES:PPS'
)

PORTFOLIO_DB_GROUP.add_option('--daily', '--dailyupdate',
    dest='LiveData',
    action='store_true',
    default=False,
    help='Update the portfolio table with live stock data.')

o.add_option_group(UTILITY_GROUP)
o.add_option_group(SHAREHOLDER_DB_GROUP)
o.add_option_group(FIRM_DB_GROUP)
o.add_option_group(TRANSACTION_DB_GROUP)

(o, args) = o.parse_args(sys.argv[1:])

#print("Parsed Options:", o) # For debugging
#print("Parsed Arguments:", args) # For debugging

__all__ = ['o', 'args']