from options import args
from database.repositories.generic import GenericRepository
from database.repositories.shareholder import ShareholderRepository

import logging

logger = logging.getLogger(__name__)

def handle_delete_by_id(db):
    try:
        repository = GenericRepository(db, args.table)
        repository.delete(args.Remove)
        logger.info(f'Entity with id: {args.Remove} from table: {args.table} deleted sucessfully.')
        
    except Exception as e:
        logger.error(f'An error occurred handling the deletion of an entity from the table: {e}')
        raise
        