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
            data = entity.to_dict()
            columns = list(data.keys())
            values = list(data.values())

            # Exclude fields with None values to allow the database to assign values.
            exclusion_fields = [key for key, value in data.items() if value is None]
            for key in exclusion_fields:
                if key in columns:
                    index = columns.index(key)
                    columns.pop(index)
                    values.pop(index)
            
            if not columns:
                raise ValueError('No fields provided for insertion. All fields are None or Null.')

            columns_str = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(values))
            query = f"INSERT INTO {self.table_name} ({columns_str}) VALUES ({placeholders}) RETURNING id"

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

    def edit(self, entity_id: int, **kwargs) -> bool:
        """Edit specific fields of a record by ID."""
        if not kwargs:
            logger.warning("No fields provided for update.")
            return False
        try:
            set_clause = ', '.join([f"{key} = %s" for key in kwargs.keys()])
            values = tuple(kwargs.values()) + (entity_id,)
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = %s"
            self.db.cursor.execute(query, values)
            self.db.connection.commit()
            return self.db.cursor.rowcount > 0
        except Exception as e:
            self.db.connection.rollback()
            logger.error(f"Error updating {self.table_name} (ID: {entity_id}): {e}")
            return False
        
    def update(self):
        pass
    
    def truncate(self):
        pass
    
    def initialize(self):
        pass
    
    def verify(self):
        pass