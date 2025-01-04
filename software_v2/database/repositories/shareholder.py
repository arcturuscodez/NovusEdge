from typing import List
from database.connection import DatabaseConnection
from database.models import ShareholderModel
from database.queries import Queries

import logging

logger = logging.getLogger(__name__)

class ShareholderRepository:
    """Handles all CRUD operations for Shareholders."""
    
    def __init__(self, db_conn: DatabaseConnection):
        self.db = db_conn
        
    def add_shareholder(self, shareholder: ShareholderModel) -> int:
        """Adds a new shareholder to the database and returns the new ID."""
        query, values = Queries.InsertIntoTableQuery(
            'SHAREHOLDERS',
            ['NAME', 'OWNERSHIP', 'INVESTMENT', 'EMAIL'],
            [shareholder.name, shareholder.ownership, shareholder.investment, shareholder.email]
        )
        self.db.cursor.execute(query, values)
        
        