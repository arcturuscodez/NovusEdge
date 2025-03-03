import argparse

def create_main_parser() -> argparse.ArgumentParser:
    """Create the main parser for NovusEdge CLI."""
    parser = argparse.ArgumentParser(
        description='NovusEdge: Investment Firm Management Tool',
        prog='novusedge',
        usage='%(prog)s [options] command [args]',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '-vsn', '--version',
        action='version',
        version='%(prog)s 0.2.3',
        help='Display the current version of the application'
    )
    parser.add_argument(
        '-o', '--override',
        action='store_true',
        help='Override existing rules, such as the daily current price update'
    )
    return parser

def add_server_parser(subparsers) -> None:
    """Add 'server' subcommand parser."""
    parser = subparsers.add_parser('server', help='Database server management')
    
    parser.add_argument(
        'action',
        choices=['start', 'stop', 'check'],
        help='Start, stop, or check the status of the database server'
    )
    
def add_create_parser(subparsers) -> None:
    """Add 'create' subcommand parser."""
    parser = subparsers.add_parser('create', help='Create a new entity')
    
    parser.add_argument(
        "type",
        choices=['shareholder', 'transaction', 'firm', 'expense', 'revenue', 'liability'],
        help='Type of entity to create'
    )
    parser.add_argument('--table',
                        type=str,
                        help='Table for generic operations'
    )
    
    parser.add_argument('--id',
                        type=int,
                        help='ID for operations requiring it'
    )
    
    parser.add_argument('--values',
                        type=str,
                        help='Entity data in key=value:key=value format (e.g. name=John:age=25)'
    )
    
def add_read_parser(subparsers) -> None:
    """Add 'read' subcommand parser."""
    parser = subparsers.add_parser('read', help='Read data from the database')
    
    parser.add_argument(
        'table',
        help='Table to read data from'
    )
    
def add_update_parser(subparsers) -> None:
    """Add ''update' subcommand parser."""
    parser = subparsers.add_parser('update', help='Update an existing entity')
    
    parser.add_argument(
        'type',
        choices=['shareholder', 'transaction', 'entity'],
        help='Type of entity to update'
    )
    
    parser.add_argument('id', 
                        type=int,
                        help='ID of the entity to update'
    )
    
    parser.add_argument('--values',
                        type=str,
                        help='Entity data in key=value:key=value format (e.g. name=John:age=25)'
    )
    
def add_delete_parser(subparsers) -> None:
    """Add 'delete' subcommand parser."""
    parser = subparsers.add_parser('delete', help='Delete an entity')
    
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
    parser = subparsers.add_parser('search', help='Search for a ticker')
    
    parser.add_argument(
        'query',
        help='Query to search for (ticker or company name)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Maximum number of results to return'
    )
    
def setup_parser() -> argparse.ArgumentParser:
    """Set up the full argument parser with all subcommands."""
    parser = create_main_parser()
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')
    
    # Register subcommands
    add_server_parser(subparsers)
    add_create_parser(subparsers)
    add_read_parser(subparsers)
    add_update_parser(subparsers)
    add_delete_parser(subparsers)
    add_search_parser(subparsers)
    
    return parser

args = setup_parser().parse_args()

if __name__ == '__main__':
    print(args)