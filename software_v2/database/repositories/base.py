# database/repositories/base_repository.py

from typing import List, Optional, Type, TypeVar, Any
from database.connection import DatabaseConnection
from database.models import BaseModel
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class BaseRepository:
    """Base repository providing common CRUD operations."""

    def __init__(self, db_conn: DatabaseConnection, table_name: str, model: Type[T]):
        self.db = db_conn
        self.table_name = table_name
        self.model = model

    def add(self, entity: T) -> Optional[int]:
        """Add a new entity to the database."""
        try:
            columns = ', '.join(entity.to_dict().keys())
            placeholders = ', '.join(['%s'] * len(entity.to_dict()))
            values = tuple(entity.to_dict().values())
            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders}) RETURNING id"
            self.db.cursor.execute(query, values)
            entity_id = self.db.cursor.fetchone()[0]
            self.db.connection.commit()
            return entity_id
        except Exception as e:
            self.db.connection.rollback()
            logger.error(f"Error adding entity to {self.table_name}: {e}")
            return None

    def fetch_all(self, columns: Optional[List[str]] = None) -> List[T]:
        """Fetch all records from the table."""
        try:
            cols = ', '.join(columns) if columns else '*'
            query = f"SELECT {cols} FROM {self.table_name}"
            self.db.cursor.execute(query)
            rows = self.db.cursor.fetchall()
            return [self.model(**dict(zip([desc[0] for desc in self.db.cursor.description], row))) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching all from {self.table_name}: {e}")
            return []

    def delete(self, entity_id: int) -> bool:
        """Delete a record by ID."""
        try:
            query = f"DELETE FROM {self.table_name} WHERE id = %s"
            self.db.cursor.execute(query, (entity_id,))
            self.db.connection.commit()
            return self.db.cursor.rowcount > 0
        except Exception as e:
            self.db.connection.rollback()
            logger.error(f"Error deleting from {self.table_name}: {e}")
            return False

    def update(self, entity_id: int, **kwargs) -> bool:
        """Update a record by ID."""
        try:
            set_clause = ', '.join([f"{key} = %s" for key in kwargs.keys()])
            values = tuple(kwargs.values()) + (entity_id,)
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = %s"
            self.db.cursor.execute(query, values)
            self.db.connection.commit()
            return self.db.cursor.rowcount > 0
        except Exception as e:
            self.db.connection.rollback()
            logger.error(f"Error updating {self.table_name}: {e}")
            return False