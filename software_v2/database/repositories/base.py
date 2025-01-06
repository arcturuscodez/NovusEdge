from typing import List, Optional, Type, TypeVar, Any
from database.connection import DatabaseConnection
from database.models import BaseModel
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class BaseRepository:
    """Base repository providing common CRUD operations."""

    def __init__(self, db_conn: DatabaseConnection, table_name: str, model: Type[T], primary_keys: List[str] = ['id']):
        self.db = db_conn
        self.table_name = table_name
        self.model = model
        self.primary_keys = primary_keys

    def add(self, entity: T) -> Optional[int]:
        """
        Add a new entity to the database.
        
        Args:
            entity (T): The entity to add.

        Returns:
            Optional[int]: The ID of the newly added entity, or None if failed.
        """
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
            logger.error(f"Error adding entity to {self.table_name}: {e}", exc_info=True)
            print("An internal error occurred while adding the entity. Please try again later.")
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
        
    def get(self, **kwargs) -> Optional[T]:
        """Get a record by primary key(s)."""
        try:
            if not kwargs:
                logger.warning("No conditions provided for fetching record.")
                return None
            conditions = ' AND '.join([f"{key} = %s" for key in kwargs.keys()])
            values = list(kwargs.values())
            query = f"SELECT * FROM {self.table_name} WHERE {conditions}"
            self.db.cursor.execute(query, values)
            row = self.db.cursor.fetchone()
            if row:
                return self.model(**dict(zip([desc[0] for desc in self.db.cursor.description], row)))
            return None
        
        except Exception as e:
            logger.error(f"Error fetching from {self.table_name} with conditions {kwargs}: {e}")
            return None
 
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
        
    def edit(self, **kwargs) -> bool:
        """Edit specific fields of a record by primary key(s)."""
        if not kwargs:
            logger.warning("No fields provided for editing.")
            return False
        try:
            update_fields = {k: v for k, v in kwargs.items() if k not in self.primary_keys}
            if not update_fields:
                logger.warning("No updatable fields provided.")
                return False
            condition_fields = {k: v for k, v in kwargs.items() if k in self.primary_keys}
            set_clause = ', '.join([f"{key} = %s" for key in update_fields.keys()])
            conditions = ' AND '.join([f"{key} = %s" for key in condition_fields.keys()])
            values = list(update_fields.values()) + list(condition_fields.values())
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE {conditions}"
            self.db.cursor.execute(query, values)
            self.db.connection.commit()
            return self.db.cursor.rowcount > 0
        
        except Exception as e:
            self.db.connection.rollback()
            logger.error(f"Error updating {self.table_name} with {kwargs}: {e}")
            return False
        
    def update(self, entity_id: int, **kwargs):
        """Update fields of a record."""
        if not kwargs:
            logger.warning('No fields provided for update.')
            pass
    
    def truncate(self):
        pass
    
    def initialize(self):
        pass
    
    def verify(self):
        pass