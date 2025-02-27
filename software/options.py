# options.py
import argparse

def software_parser():
    parser = argparse.ArgumentParser(
        description='NovusEdge: Financial Management Tool',
        prog='novusedge'
    )
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('-o', '--override', action='store_true', help='Override existing rules, such as the daily current price update.')

    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    # 'server' subcommand
    server_parser = subparsers.add_parser('server', help='Server management')
    server_parser.add_argument(
        'action',
        choices=['start', 'stop'],
        help='Server action'
    )
    
    # 'create' subcommand
    create_parser = subparsers.add_parser('create', help='Create a new entity')
    create_parser.add_argument(
        'type',
        choices=['shareholder', 'transaction', 'firm', 'expense', 'revenue', 'liability'],
        help='Type of entity to create'
    )
    create_parser.add_argument('--table', type=str, help='Table for generic operations')
    create_parser.add_argument('--id', type=int, help='ID for operations requiring it')
    create_parser.add_argument('--values', type=str, help='Data in key=value format (e.g., name=John:ownership=10)')

    # 'print' subcommand
    read_parser = subparsers.add_parser('read', help='Read table data')
    read_parser.add_argument('table', help='Table to read')

    # 'update' subcommand
    update_parser = subparsers.add_parser('update', help='Update an entity')
    update_parser.add_argument(
        'type',
        choices=['shareholder', 'transaction'],
        help='Type of entity to update'
    )
    update_parser.add_argument('id', type=int, help='ID of the entity')
    update_parser.add_argument('data', type=str, help='Data in key=value format')

    # 'delete' subcommand
    delete_parser = subparsers.add_parser('delete', help='Delete an entity')
    delete_parser.add_argument('table', help='Table to delete from')
    delete_parser.add_argument('id', type=int, help='ID of the entity')

    search_parser = subparsers.add_parser('search', help='Search for tickers or similar tickers')
    search_parser.add_argument('query', help='Search query (ticker or company name)')
    search_parser.add_argument('--limit', type=int, default=10, help='Maximum number of results to return')
    
    return parser

args = software_parser().parse_args()