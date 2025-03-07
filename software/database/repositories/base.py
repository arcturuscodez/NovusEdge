from typing import List, Optional, Type, TypeVar, Any, Dict, Union
from psycopg2 import OperationalError, IntegrityError
from database.connection import DatabaseConnection
from database.models import BaseModel
from functools import wraps
import numbers
import time

import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

def handle_db_errors(func):
    """
    Decorator to handle database errors and rollback transactions.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        max_retries = 3
        retry_delay = 2
        attempt = 0
        while attempt < max_retries:
            try:
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                execution_time = end_time - start_time
                logger.debug(f'Executed {func.__name__} in {execution_time:.2f} seconds')
                return result
            except IntegrityError as e:
                logger.error(f'Integrity error during {func.__name__}: {e}', exc_info=True)
                args[0].db.connection.rollback()
                return None
            except OperationalError as e:
                logger.warning(f'Operational error during {func.__name__}, attempt {attempt + 1}/{max_retries}: {e}', exc_info=True)
                args[0].db.connection.rollback()
                attempt += 1
                time.sleep(retry_delay)
            except Exception as e:
                logger.error(f'Database operation failed during {func.__name__}: {e}', exc_info=True)
                args[0].db.connection.rollback()
                return None
        logger.error(f'Failed to execute {func.__name__} after {max_retries} attempts')
        return None
    return wrapper

class BaseRepository:
    """
    Base repository class for CRUD operations on a table.
    """

    def __init__(self, db: DatabaseConnection, table_name: str, model: Type[T], primary_keys: List[str] = ['id']):
        """
        Initialize the repository with the database connection, table name, model and primary keys.

        Args:
            db (DatabaseConnection): The database connection object.
            table_name (str): The name of the table in the database.
            model (Type[T]): The model dataclass for the table.
            primary_keys (List[str], optional): The primary keys of the table. Defaults to ['id'].
        """
        self.db = db
        self.table_name = table_name
        self.model = model
        self.primary_keys = primary_keys
        logger.debug(f"Initialized BaseRepository for table '{table_name}' with model {model.__name__}")

    @handle_db_errors
    def create(self, entity: T) -> Optional[int]:
        """
        Create a new entity in the table.

        Args:
            entity (T): _description_

        Returns:
            Optional[int]: _description_
        """
        data = entity.to_dict()
        columns = [key for key, value in data.items() if value is not None]
        values = [value for value in data.values() if value is not None]
        if not columns:
            logger.error("No fields provided for insertion. All fields are None or Null.")
            return None
        columns_str = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(values))
        query = f'INSERT INTO {self.table_name} ({columns_str}) VALUES ({placeholders}) RETURNING {self.primary_keys[0]}'
        logger.debug(f"Executing create query: {query} with values {values}")
        self.db.cursor.execute(query, values)
        entity_id = self.db.cursor.fetchone()[0]
        logger.info(f"Created entity in {self.table_name} with ID: {entity_id}")
        return entity_id

    @handle_db_errors
    def get_entity(self, **kwargs) -> Optional[T]:
        """
        Get a single entity from the table based on the filter conditions.

        Returns:
            Optional[T]: The entity object if found, otherwise None.
        """
        if not kwargs:
            logger.warning("No filter conditions provided for fetching entity.")
            return None
        conditions = ' AND '.join([f"{key} = %s" for key in kwargs.keys()])
        values = list(kwargs.values())
        query = f'SELECT * FROM {self.table_name} WHERE {conditions} LIMIT 1'
        logger.debug(f"Fetching entity with query: {query} and values {values}")
        self.db.cursor.execute(query, values)
        row = self.db.cursor.fetchone()
        if row:
            columns = [desc[0] for desc in self.db.cursor.description]
            data = dict(zip(columns, row))
            logger.debug(f"Fetched entity from {self.table_name} with conditions {kwargs}")
            return self.model(**data)
        logger.debug(f"No entity found in {self.table_name} with conditions {kwargs}")
        return None

    @handle_db_errors
    def get_all(self, filters: Optional[Dict[str, Any]] = None, order_by: Optional[List[str]] = None, limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        """
        Get all entities from the table based on the filter conditions.

        Args:
            filters (Optional[Dict[str, Any]], optional): Dictionary of filter conditions. Defaults to None.
            order_by (Optional[List[str]], optional): List of fields to order by. Defaults to None.
            limit (Optional[int], optional): Limit the number of results. Defaults to None.
            offset (Optional[int], optional): Offset the results. Defaults to None.

        Returns:
            List[T]: List of entity objects.
        """
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
        logger.debug(f"Fetching all entities with query: {query} and values {values}")
        self.db.cursor.execute(query, values)
        rows = self.db.cursor.fetchall()
        columns = [desc[0] for desc in self.db.cursor.description]
        entities = [self.model(**dict(zip(columns, row))) for row in rows]
        logger.debug(f"Fetched {len(entities)} entities from {self.table_name}")
        return entities

    @handle_db_errors
    def update(self, entity_id: Union[int, Any], **kwargs) -> bool:
        if not kwargs:
            logger.warning(f"No fields provided for update in {self.table_name}")
            return False
        set_clause = ', '.join([f"{key} = %s" for key in kwargs.keys()])
        values = [float(value) if isinstance(value, numbers.Number) else value for value in kwargs.values()]
        if isinstance(entity_id, tuple):
            conditions = ' AND '.join([f"{pk} = %s" for pk in self.primary_keys])
            values.extend(entity_id)
        else:
            conditions = ' AND '.join([f"{pk} = %s" for pk in self.primary_keys])
            values.append(entity_id)
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {conditions}"
        logger.debug(f"Updating entity with query: {query} and values {values}")
        self.db.cursor.execute(query, values)
        success = self.db.cursor.rowcount > 0
        if success:
            logger.debug(f"Updated entity in {self.table_name} with ID: {entity_id}")
        else:
            logger.warning(f"No entity found to update in {self.table_name} with ID: {entity_id}")
        return success

    @handle_db_errors
    def delete(self, entity_id: Union[int, Any]) -> bool:
        if isinstance(entity_id, tuple):
            conditions = ' AND '.join([f"{pk} = %s" for pk in self.primary_keys])
            values = list(entity_id)
        else:
            conditions = ' AND '.join([f"{pk} = %s" for pk in self.primary_keys])
            values = [entity_id]
        query = f"DELETE FROM {self.table_name} WHERE {conditions}"
        logger.debug(f"Deleting entity with query: {query} and values {values}")
        self.db.cursor.execute(query, values)
        success = self.db.cursor.rowcount > 0
        if success:
            logger.debug(f"Deleted entity from {self.table_name} with ID: {entity_id}")
        else:
            logger.warning(f"No entity found to delete in {self.table_name} with ID: {entity_id}")
        return success

    @handle_db_errors
    def execute_raw_query(self, query: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        logger.debug(f"Executing raw query: {query} with params {params}")
        self.db.cursor.execute(query, params)
        rows = self.db.cursor.fetchall()
        columns = [desc[0] for desc in self.db.cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        logger.debug(f"Executed raw query on {self.table_name}, returned {len(results)} rows")
        return results

    @handle_db_errors
    def increment_field(self, entity_id: int, field: str, delta: float) -> bool:
        query = f"UPDATE {self.table_name} SET {field} = {field} + %s WHERE id = %s"
        logger.debug(f"Incrementing field '{field}' by {delta} for ID {entity_id} with query: {query}")
        self.db.cursor.execute(query, (delta, entity_id))
        success = self.db.cursor.rowcount > 0
        if success:
            logger.debug(f"Incremented field '{field}' by {delta} for entity ID {entity_id} in {self.table_name}")
        else:
            logger.warning(f"No entity found to increment field '{field}' for ID {entity_id} in {self.table_name}")
        return success
    
    @staticmethod
    @handle_db_errors
    def get_for_table(db: DatabaseConnection, table_name: str) -> 'BaseRepository':
        """ 
        Get Repository instance for the specified table.
        
        Args:
            db (DatabaseConnection): Database connection object
            table_name (str): Name of the table to get the repository for

        Returns:
            BaseRepository: Repository instance for the table    
        """
        try:
            table_name = table_name.upper()
            logger.debug(f'Getting repository for table: {table_name}')

            from database.repositories.shareholder import ShareholderRepository
            from database.repositories.transaction import TransactionRepository
            from database.repositories.portfolio import PortfolioRepository
            from database.repositories.firm import FirmRepository
            from database.repositories.task import TaskRepository

            repository_map = {
            'SHAREHOLDERS': ShareholderRepository,
            'TRANSACTIONS': TransactionRepository,
            'PORTFOLIO': PortfolioRepository,
            'FIRM': FirmRepository,
            'TASK_METADATA': TaskRepository
            }

            repository_class = repository_map.get(table_name)
            if repository_class:
                return repository_class(db)
            else:
                logger.warning(f'No specific repository found for table: {table_name}, using generic repository')
                return BaseRepository.for_table(db, table_name)
            
        except Exception as e:
            logger.error(f'An unexpected error occurred: {e}')
            raise

    @classmethod
    def for_table(cls, db: DatabaseConnection, table_name: str) -> 'BaseRepository':
        """
        Create a repository instance for any arbitrary table.

        This method allows working with any database table without
        requiring a dedicated repository class.
        Additionally allows the manipulation of any and all existing tables.

        Args:
            db (DatabaseConnection): Database connection object
            table_name (str): Name of the table

        Returns:
            BaseRepository: Repository instance configured for the specified table
        """
        from database.models import GenericModel
        return cls(db, table_name, GenericModel)