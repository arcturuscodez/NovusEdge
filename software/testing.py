from database_v2 import Database
from security import credentials

class Testing:
    
    def __init__(self):
        """Set up the class for database testing."""
        self.db = credentials.DB
        self.user = credentials.USER
        self.password = credentials.PASSWORD
        self.host = credentials.HOST
        self.port = credentials.PORT
        self.pg_exe = credentials.PG_EXE_PATH

        self.database = Database(
            db = self.db,
            user = self.user,
            password = self.password,
            host = self.host,
            port = self.port,
            pg_exe = self.pg_exe
        )
        
        self.test_connection()
    
    def test_connection(self):
        with self.database as connection:
            print("Successfully connected to the database.")
            connection.cursor.execute("SELECT 1;")
            result = connection.cursor.fetchone()
            assert result == (1,), "Test query failed"

Testing()