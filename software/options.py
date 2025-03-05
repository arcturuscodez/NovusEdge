import argparse
import sys
import logging
import globals

logger = logging.getLogger(__name__)

def create_main_parser() -> argparse.ArgumentParser:
    """Create the main parser for NovusEdge CLI."""
    parser = argparse.ArgumentParser(
        description='NovusEdge: Investment Firm Management Software',
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
        '-d', '--debug',
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

def add_server_parser(subparsers: argparse._SubParsersAction) -> None:
    """Add 'server' subcommand parser."""
    parser = subparsers.add_parser('server', help='NovusEdge Database Server Management')
    
    parser.add_argument(
        'action',
        choices=['start', 'stop', 'status', 'restart'],
        help='Action to perform on the server'
    )

def add_create_parser(subparsers: argparse._SubParsersAction) -> None:
    """Add 'create' subcommand parser."""
    parser = subparsers.add_parser('create', help='Create a new entity')
    
    entity_subparsers = parser.add_subparsers(
        dest='type',
        required=True,
        help='Type of entity to create'
    )
    
    entity_parsers = {
        'shareholder': ('Create a new shareholder', _create_shareholder_args),
        'transaction': ('Create a new transaction', _create_transaction_args),
        'firm': ('Create a new firm', _create_firm_args),
    }
    
    for entity_type, (help_text, add_args_func) in entity_parsers.items():
        entity_parser = entity_subparsers.add_parser(entity_type, help=help_text)
        add_args_func(entity_parser)

def _create_shareholder_args(parser: argparse.ArgumentParser) -> None:
    """Create shareholder-specific arguments."""
    parser.add_argument(
        '-n', '--name',
        dest='name',
        type=str,
        required=True,
        help='Shareholder name (required)'
    )
    
    parser.add_argument(
        '-o', '--ownership',
        dest='ownership',
        type=float,
        required=True,
        help='Firm ownership percentage (required)'
    )
    
    parser.add_argument(
        '-i', '--investment',
        dest='investment',
        type=float,
        required=True,
        help='Initial investment amount (required)'
    )
    
    parser.add_argument(
        '-e', '--email',
        dest='email',
        type=str,
        required=True,
        help='Contact email (required)'
    )

def _create_transaction_args(parser: argparse.ArgumentParser) -> None:
    """Create transaction-specific arguments."""
    parser.add_argument(
        '-t', '--ticker',
        dest='ticker',
        type=str,
        required=True,
        help='Asset ticker symbol (required)'
    )
    
    parser.add_argument(
        '-s', '--shares',
        dest='shares',
        type=float,
        required=True,
        help='Number of shares (required)'
    )
    
    parser.add_argument(
        '-p', '--pps',
        dest='price_per_share',
        type=float,
        required=True,
        help='Price per individual share (required)'
    )
    
    parser.add_argument(
        '-a', '--action',
        dest='transaction_type',
        choices=['buy', 'sell'],
        required=True,
        help='The type of transaction [buy, sell] (required)'
    )

    parser.add_argument(
        '-f', '--fees',
        dest='transaction_fees',
        type=float,
        help='Transaction fees (optional)'
    )
    
    parser.add_argument(
        '-n', '--notes',
        dest='notes',
        type=str,
        help='Additional transaction notes (optional)'
    )

def _create_firm_args(parser: argparse.ArgumentParser) -> None:
    """Create firm-specific arguments."""
    parser.add_argument(
        '-n', '--name',
        dest='firm_name',
        type=str,
        help='Firm name'
    )

def add_read_parser(subparsers: argparse._SubParsersAction) -> None:
    """Add 'read' subcommand parser."""
    parser = subparsers.add_parser('read', help='Read data from the database')
    
    parser.add_argument(
        'table',
        type=str,
        help='Table to read data from'
    )

    parser.add_argument(
        '-i', '--id',
        dest='id',
        type=int,
        help='Specific ID to read (optional)',
    )

def add_update_parser(subparsers: argparse._SubParsersAction) -> None:
    """Add 'update' subcommand parser."""
    parser = subparsers.add_parser('update', help='Update an entity in the database')

    parser.add_argument(
        'table',
        type=str,
        help='Table to update'
    )

    parser.add_argument(
        'id',
        type=int,
        help='ID of the entity to update'
    )

    parser.add_argument(
        'fields',
        nargs='+',
        help='Fields to update in the form field=value'
    )

def add_delete_parser(subparsers: argparse._SubParsersAction) -> None:
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

def add_search_parser(subparsers: argparse._SubParsersAction) -> None:
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

def parse_args() -> argparse.Namespace:
    """Parse command line arguments and return processed args."""
    parser = create_main_parser()
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    add_server_parser(subparsers)
    add_create_parser(subparsers)
    add_read_parser(subparsers)
    add_update_parser(subparsers)
    add_delete_parser(subparsers)
    add_search_parser(subparsers)
    
    args = parser.parse_args()
    return process_command_args(args)

def process_command_args(args: argparse.Namespace) -> argparse.Namespace:  
    """Process command line arguments."""
    if not hasattr(args, 'command') or not args.command:
        logger.error("No command specified. See -h, --help for available commands.")
        sys.exit(1)
    
    return args

args = parse_args()