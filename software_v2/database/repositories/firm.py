from typing import List, Optional
from database.connection import DatabaseConnection
from database.models import FirmModel
from database.queries import DatabaseQueries

import logging 

logger = logging.getLogger(__name__)

class FirmRepository:
    """Handles all CRUD operations for Firms."""
    
    def __init__(self, db_conn: DatabaseConnection):
        self.db = db_conn

    def update_cash_reserve(self, firm_id: int, amount: float) -> bool:
        try:
            return self.edit(firm_id=firm_id, CASH_RESERVE=lambda x: x + amount)
        except Exception as e:
            logger.error(f'Failed to update cash reserve: {e}')
            return False