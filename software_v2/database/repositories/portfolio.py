from typing import List, Optional
from database.repositories.base import BaseRepository
from database.models import PortfolioModel

import logging 

logger = logging.getLogger(__name__)

class PortfolioRepository(BaseRepository):
    """Repository for Portfolio-specific operations."""
    
    def __init__(self, db_conn):
        """Initialize the repository with the PortfolioModel."""
        super().__init__(db_conn, table_name='portfolio', model=PortfolioModel)