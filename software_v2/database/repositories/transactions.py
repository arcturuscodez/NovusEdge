from typing import List, Optional
from database.repositories.base import BaseRepository
from database.models import TransactionsModel

import logging

logger = logging.getLogger(__name__)

class TransactionsRepository(BaseRepository):
    """Repository for Transaction-specific operations."""
    
    def __init__(self, db_conn):
        """Initialize the repository with the TransactionsModel."""
        super().__init__(db_conn, table_name='transactions', model=TransactionsModel)