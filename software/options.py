"""Command line argument parsing for NovusEdge."""
import argparse
import sys
import globals
import logging

logger = logging.getLogger(__name__)

def create_main_parser() -> argparse.ArgumentParser:
    """Create the main parser for NovusEdge CLI."""
    parser = argparse.ArgumentParser(
        description='NovusEdge: Investment Firm Management Tool',
        prog='novusedge',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-v', '--version',
        dest='version',
        action='version',
        version=f'Version: {globals.VERSION}'
    )
    
    parser.add_argument(
        '-d' ,'--debug',
        dest='debug',
        action='store_true',
        help='Enable debugging mode'
    )
    
    parser.add_argument(
        '-o', '--override',
        dest='override',
        action='store_true',
        help='Override existing rules'
    )
    
    return parser

def add_server_parser(subparsers) -> None:
    """Add 'server' subcommand parser."""
    parser = subparsers.add_parser('server', help='NovusEdge Database Server Management')
    
    parser.add_argument(
        'action',
        choices=['start', 'stop', 'check'],
        help='Action to perform on the server'
    )
    
def add_create_parser(subparsers) -> None:
    """Add 'create' subcommand parser."""
    parser = subparsers.add_parser('create', help='Create a new entity')
    
    entity_subparsers = parser.add_subparsers(
        dest='type',
        required=True,
        help='Type of entity to create'
    ) # Subparsers for each entity type
    
    entity_parsers = {
        'shareholder': ('Create a new shareholder', _add_shareholder_args),
        'transaction': ('Create a new transaction', _add_transaction_args),
        'firm': ('Create a new firm', _add_firm_args),
    } # Entity type to help text and argument function mapping
    
    # Add subparsers for each entity type
    for entity_type, (help_text, add_args_func) in entity_parsers.items():
        entity_parser = entity_subparsers.add_parser(entity_type, help=help_text)
        add_args_func(entity_parser)

def _add_shareholder_args(parser):
    """Add shareholder-specific arguments."""
    parser.add_argument(
        '-n', '--name',
        dest='name',
        type=str,
        help='Shareholder name'
    )
    
    parser.add_argument(
        '-o','--ownership',
        dest='ownership',
        type=float,
        help='Firm ownership percentage'
    )
    
    parser.add_argument(
        '-i', '--investment',
        dest='investment',
        type=float,
        help='Initial investment amount'
    )
    
    parser.add_argument(
        '-e', '--email',
        dest='email',
        type=str,
        help='Contact email'
    )

def _add_transaction_args(parser):
    """Add transaction-specific arguments."""
    
    parser.add_argument(
        '-t' ,'--ticker',
        dest='ticker',
        type=str,
        help='Stock ticker symbol'
    )
    
    parser.add_argument(
        '-s', '--shares',
        dest='shares',
        type=float,
        help='Number of shares'
    )
    
    parser.add_argument(
        '-p', '--pps',
        dest='price_per_share',
        type=float,
        help='Price per share')
    
    parser.add_argument(
        '-a', '--action',
        dest='transaction_type',
        choices=['buy', 'sell'],
        help='Transaction type (buy/sell)'
        )
    
    parser.add_argument(
        '-n', '--notes',
        dest='notes',
        type=str,
        help='Additional transaction notes'
        )

def _add_firm_args(parser):
    """Add firm-specific arguments."""
    
    parser.add_argument(
        '-n', '--name',
        dest='firm_name',
        type=str,
        help='Firm name'
    )
    
def add_read_parser(subparsers) -> None:
    """Add 'read' subcommand parser."""
    parser = subparsers.add_parser('read', help='Read data from the database')
    
    parser.add_argument(
        'table',
        help='Table to read data from'
    )

def add_update_parser(subparsers) -> None:
    """Add 'update' subcommand parser."""
    parser = subparsers.add_parser('update', help='Update an existing entity')
    
    entity_subparsers = parser.add_subparsers(dest='type', required=True, help='Type of entity to update')
    
    # Shareholder update subparser
    shareholder_parser = entity_subparsers.add_parser('shareholder', help='Update a shareholder')
    shareholder_parser.add_argument('id', type=int, help='ID of the shareholder to update')
    _add_shareholder_args(shareholder_parser)
    
    # Transaction update subparser
    transaction_parser = entity_subparsers.add_parser('transaction', help='Update a transaction')
    transaction_parser.add_argument('id', type=int, help='ID of the transaction to update')
    _add_transaction_args(transaction_parser)

def add_delete_parser(subparsers) -> None:
    """Add 'delete' subcommand parser."""
    parser = subparsers.add_parser('delete', help='Delete an entity from the database')
    
    parser.add_argument(
        'table',
        help='Table to delete from'
    )
    
    parser.add_argument(
        'id',
        type=int,
        help='ID of the entity to delete'
    )

def add_search_parser(subparsers) -> None:
    """Add 'search' subcommand parser."""
    parser = subparsers.add_parser('search', help='Search for assets')
    
    parser.add_argument(
        'query',
        help='Search query'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Maximum number of results to return'
    )

def parse_args():
    """
    Parse command line arguments and return processed args.
    """
    parser = create_main_parser()
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add command subparsers
    add_server_parser(subparsers)
    add_create_parser(subparsers)
    add_read_parser(subparsers)
    add_update_parser(subparsers)
    add_delete_parser(subparsers)
    add_search_parser(subparsers)
    
    args = parser.parse_args()
    
    args = process_command_args(args)
    
    return args

def process_command_args(args) -> argparse.Namespace:  
    """
    Process command line arguments.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        args: Processed command line arguments
    """
    # Show help if no command provided
    if not hasattr(args, 'command') or not args.command:
        logger.error("No command specified. See --help for available commands.")
        sys.exit(1)
    
    return args

args = parse_args()