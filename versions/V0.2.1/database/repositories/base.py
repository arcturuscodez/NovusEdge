from typing import List, Optional, Type, TypeVar, Any, Dict, Union
from database.connection import DatabaseConnection
from database.models import BaseModel
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class BaseRepository:
    """Base repository providing common CRUD operations."""

    def __init__(
        self,
        db_conn: DatabaseConnection,
        table_name: str,
        model: Type[T],
        primary_keys: List[str] = ['id']
    ):
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
            columns = [key for key, value in data.items() if value is not None]
            values = [value for value in data.values() if value is not None]
            
            if not columns:
                raise ValueError('No fields provided for insertion. All fields are None or Null.')
            
            columns_str = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(values))
            query = f'INSERT INTO {self.table_name} ({columns_str}) VALUES ({placeholders}) RETURNING {self.primary_keys[0]}'
            
            with self.db as (connection, cursor):
                cursor.execute(query, values)
                entity_id = cursor.fetchone()[0]
                logger.info(f'Added entity to {self.table_name} with ID: {entity_id}')
                return entity_id

        except Exception as e:
            logger.error(f'Error adding entity to {self.table_name}: {e}', exc_info=True)
            print("An internal error occurred while adding the entity. Please try again later.")
            return None

    def get(self, **kwargs) -> Optional[T]:
        """ 
        Retrieve a single entity based on provided filters.

        Args:
            **kwargs: Field-value pairs to filter the query.

        Returns:
            Optional[T]: The entity retrieved, or None if not found.
        """
        try:
            if not kwargs:
                logger.warning('No conditions provided for fetching record.')
                return None
            
            conditions = ' AND '.join([f"{key} = %s" for key in kwargs.keys()])
            values = list(kwargs.values())
            query = f'SELECT * FROM {self.table_name} WHERE {conditions} LIMIT 1'
            
            with self.db as (connection, cursor):
                cursor.execute(query, values)
                row = cursor.fetchone()
                
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    data = dict(zip(columns, row))
                    logger.info(f'Fetched entity from {self.table_name} with conditions {kwargs}')
                    return self.model(**data)
                return None
            
        except Exception as e:
            logger.error(f'Error fetching from {self.table_name} with conditions {kwargs}: {e}', exc_info=True)
            return None

    def get_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[T]:
        """Retrieve multiple entities based on provided filters.

        Args:
            filters (Optional[Dict[str, Any]]): Field-value pairs to filter the query.
            order_by (Optional[List[str]]): Columns to order the results by.
            limit (Optional[int]): Maximum number of records to retrieve.
            offset (Optional[int]): Number of records to skip.

        Returns:
            List[T]: A list of retrieved entities.
        """
        try:
            query = f"SELECT * FROM {self.table_name}"
            values = []

            if filters:
                conditions = ' AND '.join([f"{key} = %s" for key in filters.keys()])
                query += f" WHERE {conditions}"
                values.extend(filters.values())
                
            if order_by:
                order_clause = ', '.join(order_by)
                query += f" ORDER BY {order_clause}"
                
            if limit:
                query += f" LIMIT {limit}"
                
            if offset:
                query += f" OFFSET {offset}"
                
            with self.db as (connection, cursor):
                cursor.execute(query, values)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                entities = [self.model(**dict(zip(columns, row))) for row in rows]
                logger.info(f'Fetched {len(entities)} entities from {self.table_name}')
                return entities

        except Exception as e:
            logger.error(f'Error fetching entities from {self.table_name}: {e}', exc_info=True)
            return []

    def update(self, entity_id: Union[int, Any], **kwargs) -> bool:
        """ 
        Update an existing entity with provided fields.

        Args:
            entity_id (Union[int, Any]): The ID or composite key of the entity to update.
            **kwargs: Field-value pairs to update.

        Returns:
            bool: True if update successful, False otherwise.
        """
        if not kwargs:
            logger.warning('No fields provided for update.')
            return False

        try:
            set_clause = ', '.join([f"{key} = %s" for key in kwargs.keys()])
            values = list(kwargs.values())

            if isinstance(entity_id, tuple):
                conditions = ' AND '.join([f"{pk} = %s" for pk in self.primary_keys])
                values.extend(entity_id)
            else:
                conditions = ' AND '.join([f"{pk} = %s" for pk in self.primary_keys])
                values.append(entity_id)

            query = f"UPDATE {self.table_name} SET {set_clause} WHERE {conditions}"

            with self.db as (connection, cursor):
                cursor.execute(query, values)
                success = cursor.rowcount > 0
                if success: 
                    logger.info(f'Updated entity in {self.table_name} with ID: {entity_id}')
                else:
                    logger.warning(f'No entity found to update in {self.table_name} with ID: {entity_id}')
                return success

        except Exception as e:
            logger.error(f'Error updating {self.table_name} with ID: {entity_id}: {e}', exc_info=True)
            return False

    def delete(self, entity_id: Union[int, Any]) -> bool:
        """ 
        Delete an entity based on its ID or composite key.

        Args:
            entity_id (Union[int, Any]): The ID or composite key of the entity to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            if isinstance(entity_id, tuple):
                conditions = ' AND '.join([f"{pk} = %s" for pk in self.primary_keys])
                values = list(entity_id)
            else:
                conditions = ' AND '.join([f"{pk} = %s" for pk in self.primary_keys])
                values = [entity_id]

            query = f"DELETE FROM {self.table_name} WHERE {conditions}"

            with self.db as (connection, cursor):
                cursor.execute(query, values)
                success = cursor.rowcount > 0
                if success:
                    logger.info(f"Deleted entity from {self.table_name} with ID: {entity_id}")
                else:
                    logger.warning(f"No entity found to delete in {self.table_name} with ID: {entity_id}")
                return success

        except Exception as e:
            logger.error(f'Error deleting from {self.table_name} with ID: {entity_id}: {e}', exc_info=True)
            return False

    def execute_raw_query(self, query: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a raw SQL query.

        Args:
            query (str): The SQL query to execute.
            params (Optional[List[Any]], optional): Parameters to pass with the query.

        Returns:
            List[Dict[str, Any]]: The result set as a list of dictionaries.
        """
        try:
            with self.db as (connection, cursor):
                cursor.execute(query, params)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                results = [dict(zip(columns, row)) for row in rows]
                logger.info(f'Executed raw query on {self.table_name}: {query}')
                return results

        except Exception as e:
            logger.warning(f'Error executing raw query on {self.table_name}: {e}', exc_info=True)
            return []