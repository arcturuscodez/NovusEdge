import logging
import subprocess
import time

from typing import Optional, Tuple
from psycopg2 import pool, OperationalError, DatabaseError

import psycopg2 as psy

logging.basicConfig(level=logging.INFO)

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
            pg_exe (str): The path to the PostgreSQL executuable.
            max_retries (int, optional): _description_. Defaults to 3.
            retry_delay (int, optional): _description_. Defaults to 5.
        """
        self.db = db
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self.pg_exe = pg_exe
        
        self.pool = pool.ThreadedConnectionPool(minconn, maxconn,
                                                    dbname=self.db,
                                                    user=self.user,
                                                    password=self.password,
                                                    host=self.host,
                                                    port=self.port)
        
        if not self.pool:
            logging.error('Failed to create the connection pool.')
            raise Exception('Failed to create the connection pool.')
        
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
                logging.info(f'PostgreSQL server is already running on {self.host}:{self.port}')
                return
            
            logging.info('Attempting to start PostgreSQL server...')
            subprocess.run(self.pg_exe, check=True, shell=True, timeout=60)
            logging.info('PostgreSQL server started successfully.')
        except subprocess.CalledProcessError as e:
            logging.error(f'Failed to start PostgreSQL server: {e}')
            raise
        except subprocess.TimeoutExpired as e:
            logging.error(f'Timed out trying to start PostgreSQL server: {e}')
            raise
        
    def connect(self) -> Tuple[psy.extensions.connection, psy.extensions.cursor]:
        """Acquire a connection and cursor from the pool."""
        logging.info('Attempting to acquire a connection from the pool...')
        attempt = 0
        while attempt < self.max_retries:
            try:
                connection = self.pool.getconn()
                cursor = connection.cursor()
                logging.info('Connection acquired successfully.')
                return connection, cursor
            except OperationalError as e:
                attempt += 1
                logging.error(f'Connection attempt {attempt} failed: {e}.')
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    logging.error('Failed to acquire connection after multiple attempts.')
                    raise Exception('Failed to acquire connection from the pool.') from e
            
    def close(self, connection: psy.extensions.connection, cursor: psy.extensions.cursor) -> None:
        """Release the connection and cursor back to the pool."""
        try:
            if cursor:
                cursor.close
            if connection:
                self.pool.putconn(connection)
                logging.info('Connection returned to the pool.')
        except DatabaseError as e:
            logging.error('Error releasing connection back to the pool.')
            raise
        
    def __enter__(self) -> Tuple[psy.extensions.connection, psy.extensions.cursor]: 
        self.start_server()
        return self.connect()
    
    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        connection, cursor = None, None
        try:
            connection, cursor = self.connect()
            if exc_type:
                connection.rollback()
                logging.info('Transaction rolled back due to an error.')
            else:
                connection.commit()
                logging.info('Transaction committed successfully.')
        except DatabaseError as e:
            logging.error('Error during commit/rollback.')
            raise
        finally:
            if connection and cursor:
                self.close(connection, cursor)