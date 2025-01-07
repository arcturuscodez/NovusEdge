import unittest
import os
from database.connection import DatabaseConnection
from dotenv import load_dotenv

load_dotenv()
    
DB = os.getenv('DB')
DB_USER = os.getenv('DB_USER').lower()
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
PG_EXE = os.getenv('PG_EXE')

class TestPostgreSQLConnection(unittest.TestCase):
    
    def setUp(self):
        self.db = DB
        self.user = DB_USER
        self.password = DB_PASSWORD
        self.host = DB_HOST
        self.port = DB_PORT
        self.pg_exe = PG_EXE
        
    def test_connection_pooling(self):
        with DatabaseConnection(
            db=self.db,
            user=self.user,
            password=self.password, 
            host=self.host,
            port=self.port,
            pg_exe=self.pg_exe
        ) as (conn, cursor):
            # Ensure connection and cursor are acquired
            self.assertIsNotNone(conn)
            self.assertIsNotNone(cursor)
            # Ensure the connection is open
            self.assertFalse(conn.closed, "Connection should be open when acquired from the pool.")
        
        # After exiting the context, the connection should be returned to the pool
        # The connection should still be open as it's managed by the pool
        self.assertFalse(conn.closed, "Connection should remain open after being returned to the pool.")
        
        # Optionally, acquire another connection to ensure pooling works
        with DatabaseConnection(
            db=self.db,
            user=self.user,
            password=self.password, 
            host=self.host,
            port=self.port,
            pg_exe=self.pg_exe
        ) as (conn2, cursor2):
            self.assertIsNotNone(conn2)
            self.assertIsNotNone(cursor2)
            self.assertFalse(conn2.closed, "Second connection should be open when acquired from the pool.")

if __name__ == '__main__':
    unittest.main()