import logging
import subprocess
import time

from typing import Optional

import psycopg2 as psy
from psycopg2 import OperationalError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers = [
        logging.FileHandler("connection.log"),
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
            subprocess.run(self.pg_exe, check = True, shell = True, timeout = 60)
            
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
                #logger.info('Database connection established.')
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
                #logger.info('Database cursor closed.')
            if self.connection:
                self.connection.close()
                #logger.info('Database connection closed.')
        except psy.DatabaseError as e:
            logger.error(f'Error closing database resources: {e}')
            raise
        
    def __enter__(self) -> 'DatabaseConnection':
        """Enter the runtime context related to this object."""
        self.start_server()
        return self.connect()
    
    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        """Exit the runtime context related to this object."""
        try:
            if exc_type:
                self.connection.rollback()
                logger.info('Database transaction rolled back due to an exception.')
            else:
                self.connection.commit()
        except psy.DatabaseError as e:
            logger.error(f'Database error during commit/rollback: {e}')
            raise
        finally:
            self.close()