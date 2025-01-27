from typing import Tuple
from psycopg2 import pool, OperationalError, DatabaseError, InterfaceError
import subprocess
import time
import psycopg2 as psy
import logging
import os

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """
    A class to manage connections to a PostgreSQL database.
    """
    
    def __init__(self,
                 db: str,
                 user: str,
                 password: str,
                 host: str,
                 port: int,
                 pg_exe: str,
                 max_retries: int = 3,
                 initial_retry_delay: int = 5,
                 min_conn: int = 1,
                 max_conn: int = 10,
                 max_pool_size: int = 20
                ):
        
        self.db = db
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.pg_exe = pg_exe
        self.max_retries = max_retries
        self.initial_retry_delay = initial_retry_delay
        self.min_conn = min_conn
        self.max_conn = max_conn
        self.max_pool_size = max_pool_size

        if not self._check_server_status():
            self.start_server()
            time.sleep(5)
        
        try:
            self.pool = pool.ThreadedConnectionPool(
                min_conn, max_conn,
                dbname=self.db,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            logger.info('Connection pool created successfully.')
        
        except OperationalError as e:
            logger.error(f'Operational error creating connection pool: {e}', exc_info=True)
            raise
        
        except Exception as e:
            logger.warning(f'Error creating connection pool: {e}', exc_info=True)
            raise
        
    def connect(self) -> Tuple[psy.extensions.connection, psy.extensions.cursor]:
        """
        Acquire a connection and cursor from the pool with retry logic.
        """
        attempts = 0
        delay = self.initial_retry_delay
        while attempts < self.max_retries:
            try:
                connection = self.pool.getconn()
                cursor = connection.cursor()
                logger.info(f'Connection acquired successfully for DB: {self.db} on {self.host}:{self.port}')
                return connection, cursor
            
            except (OperationalError, InterfaceError) as e:
                attempts += 1
                logger.error(f'Connection attempt {attempts} failed: {e}. Retrying in {delay} seconds.')
                time.sleep(delay)
                delay *= 2
                
            except DatabaseError as e:
                logger.error(f'Database error acquiring connection: {e}', exc_info=True)
                raise
            
            except Exception as e:
                logger.error(f'Unexpected error acquiring connection: {e}', exc_info=True)
                raise
        
        logger.error(f'Failed to acquire connection after {attempts} attempts.')
        raise Exception('Failed to acquire connection from the pool.')
    
    def _check_server_status(self) -> bool:
        """
        Check if PostgreSQL server is running.
        """
        try:
            env = os.environ.copy()
            env['DB_PASS'] = self.password
            
            result = subprocess.run(
                ['pg_isready',
                 '-h', self.host,
                 '-p', str(self.port),
                 '-U', self.user,
                 '-d', self.db
                 ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
                env=env
            )
            is_running = result.returncode == 0
            if is_running:
                logger.info('PostgreSQL server is running.')
            else:
                logger.warning('PostgreSQL server is not running.')
            return is_running
        
        except subprocess.TimeoutExpired:
            logger.warning('Timeout while checking PostgreSQL server status.')
            return False
    
    def start_server(self) -> None:
        """ 
        Start the PostgreSQL server.
        """
        if not self._check_server_status():
            try:
                logger.warning('Attempting to start PostgreSQL server...')
                
                env = os.environ.copy()
                env['DB_PASS'] = self.password
                
                subprocess.run(['pg_ctl', 'start', '-D', self.pg_exe], check=True, timeout=30)
                logger.info('PostgreSQL server started successfully.')
            
            except subprocess.CalledProcessError as e:
                logger.error(f'Error starting PostgreSQL server: {e}', exc_info=True)
                raise RuntimeError('Error starting PostgreSQL server.')
            
            except subprocess.TimeoutExpired:
                logger.error('Timeout while starting PostgreSQL server.')
                raise RuntimeError('Timeout while starting PostgreSQL server.')
    
    def close(self, connection: psy.extensions.connection, cursor: psy.extensions.cursor) -> None:
        """
        Close the connection and cursor and return them to the pool.

        Args:
            connection (psy.extensions.connection): connection object to be closed.
            cursor (psy.extensions.cursor): cursor object to be closed.
        """
        try:
            if cursor:
                cursor.close()
            if connection:
                self.pool.putconn(connection)
                logger.info('Connection returned to the pool.')
        
        except DatabaseError as e:
            logger.error(f'Error closing connection: {e}', exc_info=True)
            raise
    
    def __enter__(self) -> Tuple[psy.extensions.connection, psy.extensions.cursor]:
        """
        Enter the runtime context for the database connection.

        Returns:
            Tuple[psy.extensions.connection, psy.extensions.cursor]: The connection and cursor objects.
        """
        self.connection, self.cursor = self.connect()
        return self.connection, self.cursor
    
    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        """ 
        Exit the runtime context for the database connection.
        """
        if self.connection and self.cursor:
            try:
                if exc_type:
                    self.connection.rollback()
                    logger.info('Transaction rolled back due to an error.')
                else: 
                    self.connection.commit()
                    logger.info('Transaction committed successfully.')
            
            except DatabaseError as e:
                logger.error(f'Error committing transaction: {e}', exc_info=True)
                
            finally:
                self.close(self.connection, self.cursor)
                self.connection = None
                self.cursor = None
                
    def adjust_pool_size(self, new_size: int) -> None:
        """ 
        Adjust the size of the connection pool.
        """
        if new_size > self.max_pool_size:
            new_size = self.max_pool_size
        self.pool.minconn = min(self.min_conn, new_size)
        self.pool.maxconn = new_size
        logger.info(f'Connection pool size adjusted to {new_size}.')
        
    def stop_server(self) -> None:
        """Stop the PostgreSQL server."""
        try:
            subprocess.run(['pg_ctl', '-D', self.pg_exe, 'stop', '-m', 'fast'], check=True, timeout=30)
            logger.info('PostgreSQL server stopped successfully.')
        except subprocess.CalledProcessError as e:
            logger.error(f'Failed to stop PostgreSQL server: {e.output.decode()}')
            raise RuntimeError("Failed to stop PostgreSQL server") from e
        except subprocess.TimeoutExpired:
            logger.error('Timed out while trying to stop PostgreSQL server.')
            raise RuntimeError("Timed out stopping PostgreSQL server")

    def manual_rollback(self, connection: psy.extensions.connection, error_msg: str = None) -> None:
        """
        Manually rollback a transaction on the provided connection.
        """
        try:
            connection.rollback()
            logger.info('Transaction rolled back successfully.')
            if error_msg:
                logger.error(error_msg)
            
        except DatabaseError as e:
            logger.error(f'Error rolling back transaction: {e}', exc_info=True)
            raise
    
    def get_connection_and_cursor(self) -> Tuple[psy.extensions.connection, psy.extensions.cursor]:
        """ 
        Get a connection and cursor from the pool.
        """
        try:
            connection = self.pool.getconn()
            logger.info(f'Connection extended successfully for DB: {self.db} on {self.host}:{self.port}')
            cursor = connection.cursor()
            return connection, cursor
        
        except DatabaseError as e:
            logger.error(f'Error extending connection: {e}', exc_info=True)
            raise
    