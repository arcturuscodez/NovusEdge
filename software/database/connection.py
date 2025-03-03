"""Database connection management module."""
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

        logger.debug(f"Initializing DatabaseConnection: db={db}, host={host}, port={port}")
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
            logger.debug(f"Connection pool created successfully for DB: {self.db} with {max_conn} max connections")

        except OperationalError as e:
            logger.error(f"Operational error creating connection pool: {e}", exc_info=True)
            raise
        
        except Exception as e:
            logger.error(f"Unexpected error creating connection pool: {e}", exc_info=True)
            raise
        
    def connect(self) -> Tuple[psy.extensions.connection, psy.extensions.cursor]:
        """
        Acquire a connection and cursor from the pool with retry logic.
        """
        attempts = 0
        delay = self.initial_retry_delay
        while attempts < self.max_retries:
            try:
                logger.debug(f"Attempting to acquire connection (attempt {attempts + 1}/{self.max_retries})")
                connection = self.pool.getconn()
                cursor = connection.cursor()
                logger.info(f"Connection acquired successfully for DB: {self.db} on {self.host}:{self.port}")
                return connection, cursor
            
            except (OperationalError, InterfaceError) as e:
                attempts += 1
                logger.warning(f"Connection attempt {attempts} failed: {e}. Retrying in {delay} seconds")
                time.sleep(delay)
                delay *= 2
                
            except DatabaseError as e:
                logger.error(f"Database error acquiring connection: {e}", exc_info=True)
                raise
            
            except Exception as e:
                logger.error(f"Unexpected error acquiring connection: {e}", exc_info=True)
                raise
        
        logger.error(f"Failed to acquire connection after {self.max_retries} attempts")
        raise Exception(f"Failed to acquire connection from the pool after {self.max_retries} attempts")
    
    def _check_server_status(self) -> bool:
        """
        Check if PostgreSQL server is running.
        """
        try:
            logger.debug(f"Checking PostgreSQL server status on {self.host}:{self.port}")
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
                logger.debug(f"PostgreSQL server is running on {self.host}:{self.port}")
            else:
                logger.warning(f"PostgreSQL server is not running on {self.host}:{self.port}")
            return is_running
        
        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout while checking PostgreSQL server status on {self.host}:{self.port}")
            return False
    
    def start_server(self) -> None:
        """ 
        Start the PostgreSQL server.
        """
        if not self._check_server_status():
            try:
                logger.info(f"Attempting to start PostgreSQL server at {self.pg_exe}")
                env = os.environ.copy()
                env['DB_PASS'] = self.password
                
                subprocess.run(['pg_ctl', 'start', '-D', self.pg_exe], check=True, timeout=30)
                logger.info("PostgreSQL server started successfully")
            
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to start PostgreSQL server: {e}", exc_info=True)
                raise RuntimeError("Error starting PostgreSQL server")
            
            except subprocess.TimeoutExpired:
                logger.error(f"Timeout while starting PostgreSQL server at {self.pg_exe}")
                raise RuntimeError("Timeout while starting PostgreSQL server")
    
    def close(self, connection: psy.extensions.connection, cursor: psy.extensions.cursor) -> None:
        """
        Close the connection and cursor and return them to the pool.

        Args:
            connection (psy.extensions.connection): Connection object to be closed.
            cursor (psy.extensions.cursor): Cursor object to be closed.
        """
        try:
            if cursor:
                logger.debug("Closing database cursor")
                cursor.close()
            if connection:
                self.pool.putconn(connection)
                logger.info(f"Connection returned to pool for DB: {self.db}")
        
        except DatabaseError as e:
            logger.error(f"Error closing connection: {e}", exc_info=True)
            raise
    
    def __enter__(self) -> Tuple[psy.extensions.connection, psy.extensions.cursor]:
        """
        Enter the runtime context for the database connection.

        Returns:
            Tuple[psy.extensions.connection, psy.extensions.cursor]: The connection and cursor objects.
        """
        try:
            logger.debug("Entering database connection context")
            self.connection, self.cursor = self.connect()
            return self.connection, self.cursor

        except Exception as e:
            logger.error(f"Error entering database connection context: {e}", exc_info=True)
            raise
    
    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        """ 
        Exit the runtime context for the database connection.
        
        Args:
            exc_type: The type of exception raised.
            exc_value: The exception value.
            exc_traceback: The traceback for the exception.
        """
        if self.connection is None or self.connection.closed:
            logger.warning("Connection already closed; skipping commit/rollback")
            return
        
        try:
            if exc_type:
                self.connection.rollback()
                logger.info("Transaction rolled back due to an error")
            else: 
                self.connection.commit()
                logger.info("Transaction committed successfully")
        
        except DatabaseError as e:
            logger.error(f"Error committing transaction: {e}", exc_info=True)
        
        except Exception as e:
            logger.error(f"Unexpected error committing transaction: {e}", exc_info=True)
            
        finally:
            self.close(self.connection, self.cursor)
            logger.debug("Exited database connection context")
            self.connection = None
            self.cursor = None
                
    def adjust_pool_size(self, new_size: int) -> None:
        """ 
        Adjust the size of the connection pool.
        """
        try:
            logger.debug(f"Adjusting connection pool size to {new_size}")
            if new_size > self.max_pool_size:
                logger.warning(f"Requested pool size {new_size} exceeds max_pool_size {self.max_pool_size}; capping at {self.max_pool_size}")
                new_size = self.max_pool_size
            self.pool.minconn = min(self.min_conn, new_size)
            self.pool.maxconn = new_size
            logger.info(f"Connection pool size adjusted to {new_size}")
            
        except Exception as e:
            logger.error(f"Error adjusting connection pool size to {new_size}: {e}", exc_info=True)
            raise
        
    def stop_server(self) -> None:
        """Stop the PostgreSQL server."""
        try:
            logger.info("Attempting to stop PostgreSQL server")
            result = subprocess.run(
                ['pg_ctl', '-D', self.pg_exe, 'stop', '-m', 'fast'], 
                check=True, 
                timeout=30,
                capture_output=True
            )
            logger.info("PostgreSQL server stopped successfully")

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else "Unknown error"
            if "Operation not permitted" in error_msg:
                logger.warning("Cannot stop PostgreSQL server: insufficient permissions")
                logger.info("Please use the PostgreSQL admin console or services panel to stop the server")
            else:
                logger.error(f"Failed to stop PostgreSQL server: {error_msg}", exc_info=True)
            raise RuntimeError("Please use the PostgreSQL admin console or services panel to stop the server")

        except subprocess.TimeoutExpired:
            logger.error("Timed out while trying to stop PostgreSQL server")
            raise RuntimeError("Timed out stopping PostgreSQL server")

    def manual_rollback(self, connection: psy.extensions.connection, error_msg: str = None) -> None:
        """
        Manually rollback a transaction on the provided connection.
        """
        try:
            logger.debug("Performing manual rollback")
            connection.rollback()
            logger.info("Transaction rolled back successfully")
            if error_msg:
                logger.error(f"Rollback triggered by: {error_msg}")
            
        except DatabaseError as e:
            logger.error(f"Error rolling back transaction: {e}", exc_info=True)
            raise
    
    def get_connection_and_cursor(self) -> Tuple[psy.extensions.connection, psy.extensions.cursor]:
        """ 
        Get a connection and cursor from the pool.
        """
        try:
            logger.debug("Extending connection from pool")
            connection = self.pool.getconn()
            cursor = connection.cursor()
            logger.info(f"Connection extended successfully for DB: {self.db} on {self.host}:{self.port}")
            return connection, cursor
        
        except DatabaseError as e:
            logger.error(f"Error extending connection: {e}", exc_info=True)
            raise