import logging
import subprocess
import time

from contextlib import contextmanager
from typing import Optional

from queries import Queries
from utility import helpers

import psycopg2 as psy
from psycopg2 import OperationalError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers = [
        logging.FileHandler("database_connection.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """
    A class for managing and manipulating the database connection.
    """
    
    def __init__(
        self,
        db: str,
        user: str,
        password: str,
        host: str,
        port: int,
        pg_exe: str,
        max_retries: int = 3,
        retry_delay: int = 5 
    ):
        """ 
        Initialize the DatabaseConnection class.
        
        Args:
            db (str): The name of the database.
            user (str): The username for the database connection.
            password (str): The password for the database connection.
            host (str): The host for the database connection.
            port (int): The port for the database connection.
            pg_exe (str): The path to the PostgreSQL executable.
            max_retries (int): The maximum number of connection retries.
            retry_delay (int): The delay between connection retries in seconds.
        """
        self.db = db
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.pg_exe = pg_exe
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self.connection: Optional[psy.extensions.connection] = None
        self.cursor: Optional[psy.extensions.cursor] = None
        
    def start_server(self) -> None:
        """Start the PostgreSQL server."""
        try:
            result = subprocess.run(
                ['pg_isready', '-h', self.host, '-p', str(self.port)],
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                check = False # Do not raise an exception on a non-zero exit code.
            )
            if result.returncode == 0:
                logger.info(f'PostgreSQL server is already running on {self.host}:{self.port}.')
                return
            logger.info('Attempting to start PostgreSQL server...')
            subprocess.run(
                [self.pg_exe],
                check = True,
                timeout = 60
            )
            logger.info('PostgreSQL server started successfully.')
        except subprocess.CalledProcessError as e:
            logger.error(f'Failed to start PostgreSQL server: {e}')
            raise
        except subprocess.TimeoutExpired as e:
            logger.error(f'Timed out trying to start PostgreSQL server: {e}')
            raise
        
    def connect(self) -> 'DatabaseConnection':
        """Attempt to establish a database connection."""
        attempt = 0
        while attempt < self.max_retries:
            try:
                self.connection = psy.connect(
                    dbname = self.db,
                    user = self.user,
                    password = self.password,
                    host = self.host,
                    port = self.port
                )
                self.cursor = self.connection.cursor()
                logger.info('Database connection established.')
                return self
            except OperationalError as e:
                attempt += 1
                logger.warning(f'Attempt {attempt} failed to connect to the database: {e}')
                if attempt < self.max_retries:
                    logger.info(f'Retrying in {self.retry_delay} seconds...')
                    time.sleep(self.retry_delay)
                else:
                    logger.error('Maximum connection attempts reached.')
                    raise Exception('Failed to connect to the database after multiple attempts.') from e
                
    def close(self) -> None:
        """Close the database connection and cursor."""
        try:
            if self.cursor:
                self.cursor.close()
                logger.info('Database cursor closed.')
            if self.connection:
                self.connection.close()
                logger.info('Database connection closed.')
        except psy.DatabaseError as e:
            logger.error(f'Error closing database resources: {e}')
            raise
        
    def __enter__(self) -> 'DatabaseConnection':
        """Enter the runtime context related to this object."""
        return self.connect()
    
    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        """Exit the runtime context related to this object."""
        try:
            if exc_type:
                if self.connection:
                    self.connection.rollback()
                    logger.info('Database transaction rolled back due to an exception.')
            else:
                if self.connection:
                    self.connection.commit()
                    logger.info('Database transaction committed successfully.')
        except psy.DatabaseError as e:
            logger.error(f'Database error during commit/rollback: {e}')
            raise
        finally:
            self.close()
            
    def fetch_data(
        self,
        table_name: str,
        columns: Optional[list] = None,
        condition: Optional[str] = None,
        condition_value: Optional[any] = None,
        print_data: bool = False
    ) -> Optional[list]:
        """ 
        Fetch data from a specified table with optional columns, condition, and printing.
        
        Args:
            table_name (str): Name of the table to fetch data from.
            columns (list, optional): List of columns to fetch. Fetches all columns if None.
            condition (str, optional): Column name for the WHERE condition.
            condition_value (any, optional): Value for the WHERE condition.
            print_data (bool, optional): Whether to print the fetched data. Default is False.
            
        Returns:
            List: List of fetched rows. Returns None if print_data is True or no data is found.
        """
        try:
            query = Queries.FetchTableDataQuery(table_name, columns, condition)
            if condition and condition_value is not None:
                self.cursor.execute(query, (condition_value,))
            else:
                self.cursor.execute(query)
                
            data = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
            
            if not data:
                print(f'No data to display from {table_name}')
                return None
            
            if print_data:
                helpers.FormatTableData(columns, data)
                return None
            
            return data
        
        except psy.errors.UndefinedTable as e:
            print(f'A database error occurred when fetching data: {e}')
        except psy.DatabaseError as e:
            print(f'A database error occurred when fetching data: {e}')
        except ValueError as e:
            print(f'Value error: {e}')
        except Exception as e:
            print(f'An unexpected error occured: {e}')
        finally:
            self.connection.rollback()

    def update_table(
        self,
        table_name: str,
        columns: list, 
        values: list, 
        condition_column: Optional[str] = None,
        condition_value: Optional[any] = None
    ) -> None:
        """
        Updates specified columns in a table based on the provided arguments.

        Args:
            table_name (str): The name of the table to update.
            columns (list): List of columns to update.
            values (list): List of values corresponding to the columns.
            condition_column (str, optional): The column to use as the WHERE condition. Defaults to None.
            condition_value (any, optional): The value for the condition column. Defaults to None.

        Returns:
            None
        """
        try:
            set_clause = ', '.join([f"{col} = %s" for col in columns])
            query = f"UPDATE {table_name} SET {set_clause}"
            values_tuple = tuple(values)
            if condition_column and condition_value is not None:
                query += f" WHERE {condition_column} = %s"
                values_tuple += (condition_value,)
            logger.debug(f'Executing update query: {query} with values: {values_tuple}')
            self.cursor.execute(query, values_tuple)
            self.connection.commit()
            logger.info(f"Updated records in {table_name} where {condition_column} = {condition_value}.")
        except psy.DatabaseError as e:
            logger.error(f"Database error during update: {e}")
            self.connection.rollback()
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during update: {e}")
            self.connection.rollback()
            raise