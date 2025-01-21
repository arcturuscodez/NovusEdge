from typing import Optional, Tuple
from psycopg2 import pool, OperationalError, DatabaseError

import subprocess
import time
import psycopg2 as psy

import logging

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """
    A class to represent a connection to a PostgreSQL database.
    """
    
    def __init__(self, db: str,
                 user: str,
                 password: str,
                 host: str,
                 port: int,
                 pg_exe: str,
                 max_retries: int = 3,
                 retry_delay: int = 5,
                 minconn: int = 1,
                 maxconn: int = 10):
        """
        Initialize the Connection class

        Args:
            db (str): The name of the database.
            user (str): The user for the database connection.
            password (str): The password for the database connection.
            host (str): The host for the database connection.
            port (int): The port for the database connection.
            pg_exe (str): The path to the PostgreSQL executable.
            max_retries (int, optional): Maximum number of connection retries. Defaults to 3.
            retry_delay (int, optional): Delay between retries in seconds. Defaults to 5.
            minconn (int, optional): Minimum number of connections in the pool. Defaults to 1.
            maxconn (int, optional): Maximum number of connections in the pool. Defaults to 10.
        """
        if not user:
            logger.error('Database user is not provided.')
            raise ValueError('Database user is required.')
        
        self.db = db
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self.pg_exe = pg_exe
        
        try:
            self.pool = pool.ThreadedConnectionPool(
                minconn, maxconn,
                dbname=self.db,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            logger.info('Connection pool created successfully.')
            
        except Exception as e:
            self.pool = None
            logger.error(f'Failed to create the connection pool: {e}', exc_info=True)
        
    def start_server(self) -> None:
        """Start the PostgreSQL server."""
        try:
            result = subprocess.run(
                ['pg_isready', '-h', self.host, '-p', str(self.port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            if result.returncode == 0:
                logger.info(f'PostgreSQL server is already running on {self.host}:{self.port}')
                return
            
            logger.info('Attempting to start PostgreSQL server...')
            subprocess.run(self.pg_exe, check=True, shell=True, timeout=60)
            logger.info('PostgreSQL server started successfully.')
        except subprocess.CalledProcessError as e:
            logger.error(f'Failed to start PostgreSQL server: {e}')
            raise
        except subprocess.TimeoutExpired as e:
            logger.error(f'Timed out trying to start PostgreSQL server: {e}')
            raise
        
    def stop_server(self) -> None:
        """Stop the PostgreSQL server."""
        try:
            pass
        except Exception as e:
            print(f'Failed to stop PostgreSQL server: {e}')
        
    def connect(self) -> Tuple[psy.extensions.connection, psy.extensions.cursor]:
        """Acquire a connection and cursor from the pool."""
        logger.info('Attempting to acquire a connection from the pool...')
        attempt = 0
        while attempt < self.max_retries:
            try:
                connection = self.pool.getconn()
                cursor = connection.cursor()
                logger.info('Connection acquired successfully.')
                logger.info(f'Connection to DB: {self.db} on {self.host}:{self.port} with role {self.user}')
                return connection, cursor
            except OperationalError as e:
                attempt += 1
                logger.error(f'Connection attempt {attempt} failed: {e}.')
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    logger.error('Failed to acquire connection after multiple attempts.')
                    raise Exception('Failed to acquire connection from the pool.') from e
            
    def close(self, connection: psy.extensions.connection, cursor: psy.extensions.cursor) -> None:
        """Release the connection and cursor back to the pool."""
        try:
            if cursor:
                cursor.close
            if connection:
                self.pool.putconn(connection)
                logger.info('Connection returned to the pool.')
        except DatabaseError as e:
            logger.error('Error releasing connection back to the pool.')
            raise
        
    def __enter__(self) -> Tuple[psy.extensions.connection, psy.extensions.cursor]: 
        """Enter the runtime context for the connection."""
        self.start_server()
        self.connection, self.cursor = self.connect()
        return self.connection, self.cursor
    
    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        if self.connection and self.cursor:
            try:
                if exc_type or exc_value or exc_traceback:
                    self.connection.rollback()
                    logger.info('Transaction rolled back due an error.')
                else:
                    self.connection.commit()
                    logger.info('Transaction committed successfully.')
            except DatabaseError as e:
                logger.error('Error during commit/rollback.', exc_info=True)
                raise
            finally:
                self.close(self.connection, self.cursor)
                self.connection = None
                self.cursor = None
                