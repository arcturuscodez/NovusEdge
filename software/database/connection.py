"""Database connection management module."""
from typing import Tuple
from psycopg2 import pool, OperationalError, DatabaseError, InterfaceError
import psycopg2 as psy
import subprocess
import socket
import struct
import time
import logging

logger = logging.getLogger(__name__)

class DatabaseServer:
    """
    A class to manage PostgreSQL server operations.
    """
    def __init__(self,
                 host: str,
                 port: int,
                 pg_exe: str) -> None:
        
        self.port = port
        self.host = host
        self.pg_exe = pg_exe

    def start(self) -> None:
        """ 
        Start the PostgreSQL server.
        """
        if not self.status():
            try:  
                subprocess.run(['pg_ctl', 'start', '-D', self.pg_exe], check=True, timeout=30)
                logger.info("PostgreSQL server started successfully")
            
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr.decode() if e.stderr else "Unknown error"
                if "another server might be running" in error_msg:
                    logger.warning("Cannot start PostgreSQL server: another server is running")
                    return
                else:
                    logger.error(f"Failed to start PostgreSQL server: {error_msg}", exc_info=True)
                    return

    def status(self, host: str = None, port: int = None) -> bool:
        """
        Check if PostgreSQL server is running by attempting a connection.

        Args:
            host (str, optional): The host to check.
            port (int, optional): The port to check.

        Returns:
            bool: True if the server is running, False otherwise.
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((str(self.host), int(self.port)))
            s.sendall(struct.pack('!i', 8))
            s.sendall(struct.pack('!i', 80877103))
            response = s.recv(1)
            s.close()
            if response in (b'S', b'N'):
                logger.info(f"PostgreSQL server is running on {self.host}:{self.port}")
                return True
            return False
        except socket.error as e:
            logger.warning(f"PostgreSQL server is not running on {self.host}:{self.port}: {e}")
            return False

    def stop(self) -> bool:
        """Stop the PostgreSQL server."""
        try:
            subprocess.run(['pg_ctl', 'stop', '-D', self.pg_exe], check=True, timeout=30)
            logger.info("PostgreSQL server stopped successfully")
            return True
        
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else "Unknown error"
            logger.error(f"Failed to stop PostgreSQL server: {error_msg}", exc_info=True)
            return False

        except Exception as e:
            logger.error(f"Unexpected error stopping PostgreSQL server: {e}", exc_info=True)
            return False
        
    def restart(self) -> bool:
            """Restart the PostgreSQL server."""
            if self.stop():
                self.start()
                return True
            else:
                return False
    
class DatabaseConnection(DatabaseServer):
    """
    A class to manage connections to a PostgreSQL database.
    """
    
    def __init__(self,
                 dbname: str,
                 username: str,
                 password: str,
                 host: str,
                 port: int,
                 max_retries: int = 3,
                 initial_retry_delay: int = 5,
                 min_conn: int = 1,
                 max_conn: int = 10,
                 max_pool_size: int = 20
                ):
        self.dbname = dbname
        self.username = username
        self.password = password
        self.host = host
        self.port = port

        self.max_retries = max_retries
        self.initial_retry_delay = initial_retry_delay

        self.min_conn = min_conn
        self.max_conn = max_conn
        self.max_pool_size = max_pool_size

        logger.debug(f"Initializing DatabaseConnection: db={self.dbname}, host={self.host}, port={self.port}")

        try:
            self.pool = pool.ThreadedConnectionPool(
                min_conn, max_conn,
                dbname=self.dbname,
                user=self.username,
                password=self.password,
                host=self.host,
                port=self.port
            ) 
            logger.debug(f"Connection pool created successfully for DB: {self.dbname} with {max_conn} max connections")

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
        if not super().status():
            self.start()
            time.sleep(5)
        return self._retry(self._acquire_connection)
    
    def _acquire_connection(self):
        connection = self.pool.getconn()
        cursor = connection.cursor()
        logger.info(f'Connection acquired successfully for DB: {self.dbname} on {self.host}:{self.port}')
        return connection, cursor
    
    def _retry(self, func):
            attempts = 0
            delay = self.initial_retry_delay
            while attempts < self.max_retries:
                try:
                    logger.debug(f"Attempting to acquire connection (attempt {attempts + 1}/{self.max_retries})")
                    return func()
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
            quit(1)
    
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
                logger.info(f"Connection returned to pool")
        
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
            return self

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
                logger.error(f"Transaction rolled back due to an error: {exc_value}")
            else: 
                self.connection.commit()
                logger.debug("Transaction committed successfully")
        
        except DatabaseError as e:
            logger.error(f"Error committing transaction: {e}", exc_info=True)
        
        except Exception as e:
            logger.error(f"Unexpected error committing transaction: {e}", exc_info=True)
            
        finally:
            self.close(self.connection, self.cursor)
            logger.debug("Exited database connection context")
            self.connection = None
            self.cursor = None

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
            logger.info(f"Connection extended successfully for DB: {self.dbname} on {self.host}:{self.port}")
            return connection, cursor
        
        except DatabaseError as e:
            logger.error(f"Error extending connection: {e}", exc_info=True)
            raise