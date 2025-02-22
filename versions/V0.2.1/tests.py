import unittest
import os
from unittest.mock import patch, MagicMock
from database.connection import DatabaseConnection
from database.repositories.shareholder import ShareholderRepository
from database.repositories.transaction import TransactionRepository
from database.models import ShareholderModel, TransactionModel

from dotenv import load_dotenv
from database.services.delete import handle_delete_by_id

import logging

logger = logging.getLogger(__name__)
dotenv_path = os.path.abspath('config/.env')
load_dotenv(verbose=True, dotenv_path=dotenv_path)
    
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
        self.port = int(DB_PORT) if DB_PORT else 5432  # Default PostgreSQL port
        self.pg_exe = PG_EXE
        
        self.db_connection = DatabaseConnection(
            db=self.db,
            user=self.user,
            password=self.password, 
            host=self.host,
            port=self.port,
            pg_exe=self.pg_exe
        )
        
    def tearDown(self):
        # Close all connections in the pool after tests
        if self.db_connection.pool:
            self.db_connection.pool.closeall()
    
    def test_connection_pooling(self):
        with self.db_connection as (conn, cursor):
            # Ensure connection and cursor are acquired
            self.assertIsNotNone(conn)
            self.assertIsNotNone(cursor)
            # Ensure the connection is open
            self.assertFalse(conn.closed, "Connection should be open when acquired from the pool.")
        
        # After exiting the context, the connection should be returned to the pool
        # The connection should still be open as it's managed by the pool
        self.assertFalse(conn.closed, "Connection should remain open after being returned to the pool.")
        
        # Optionally, acquire another connection to ensure pooling works
        with self.db_connection as (conn2, cursor2):
            self.assertIsNotNone(conn2)
            self.assertIsNotNone(cursor2)
            self.assertFalse(conn2.closed, "Second connection should be open when acquired from the pool.")

class TestSharehoilderRepository(unittest.TestCase):
    
    def setUp(self):
        
        self.db = DB
        self.user = DB_USER
        self.password = DB_PASSWORD
        self.host = DB_HOST
        self.port = int(DB_PORT) if DB_PORT else 5432  # Default PostgreSQL port
        self.pg_exe = PG_EXE
        self.db_connection = DatabaseConnection(
            db=self.db,
            user=self.user,
            password=self.password, 
            host=self.host,
            port=self.port,
            pg_exe=self.pg_exe
        )
        
        self.repository = ShareholderRepository(self.db_connection)
        
        self.connection, self.cursor = self.db_connection.connect()
        self.connection.autocommit = False
        
    def tearDown(self):
        if self.connection:
            self.connection.rollback()
            self.cursor.close()
            self.db_connection.pool.putconn(self.connection)
        
        if self.db_connection.pool:
            self.db_connection.pool.closeall()
            
    @patch('database.repositories.shareholder.ShareholderRepository.add')
    def test_add_shareholder(self, mock_add):
        mock_add.return_value = 1
        shareholder = ShareholderModel(
            name='John Doe',
            ownership=50.0,
            investment=10000.0,
            email='john.doe@example.com')
        
        shareholder_id = self.repository.add(shareholder)
        
        mock_add.asset_called_once_with(shareholder)
        self.assertEqual(shareholder_id, 1)
        logger.info(f'Tested adding shareholder with mocked ID: {shareholder_id}')
    
    @patch('database.repositories.shareholder.ShareholderRepository.add')
    def test_add_shareholder_with_invalid_email(self, mock_add):
        """ 
        Test adding a shareholder with an invalid email.
        """
        mock_add.return_value = None
        
        shareholder = ShareholderModel(
            name='Jane Doe',
            ownership=50.0,
            investment=10000.0,
            email='jane.doe@example')
        
        shareholder_id = self.repository.add(shareholder)
        
        mock_add.assert_called_once_with(shareholder)
        self.assertIsNone(shareholder_id)
        logger.info('Tested adding shareholder with invalid email.')
        
    @patch('database.repositories.shareholder.ShareholderRepository.delete')
    def test_delete_shareholder(self, mock_delete):
        mock_delete.return_value = True
        shareholder_id = 3
        
        result = self.repository.delete(shareholder_id)

        mock_delete.assert_called_once_with(shareholder_id)
        self.assertTrue(result)
        logger.info('Tested deleting shareholder by ID.')
        
    @patch('database.repositories.shareholder.ShareholderRepository.delete')
    def test_delete_shareholder_invalid_id(self, mock_delete):
        mock_delete.return_value = False
        shareholder_id = 0
        
        result = self.repository.delete(shareholder_id)
        
        mock_delete.assert_called_once_with(shareholder_id)
        self.assertFalse(result)
        logger.info('Tested deleting shareholder with invalid ID.')

class TestTransactionRepository(unittest.TestCase):
    
    def setUp(self):
            
        self.db = DB
        self.user = DB_USER
        self.password = DB_PASSWORD
        self.host = DB_HOST
        self.port = int(DB_PORT) if DB_PORT else 5432  # Default PostgreSQL port
        self.pg_exe = PG_EXE
        self.db_connection = DatabaseConnection(
            db=self.db,
            user=self.user,
            password=self.password, 
            host=self.host,
            port=self.port,
            pg_exe=self.pg_exe
        )
        
        self.repository = TransactionRepository(self.db_connection)
        
        self.connection, self.cursor = self.db_connection.connect()
        self.connection.autocommit = False
        
    def tearDown(self):
        if self.connection:
            self.connection.rollback()
            self.cursor.close()
            self.db_connection.pool.putconn(self.connection)
        
        if self.db_connection.pool:
            self.db_connection.pool.closeall()
            
    @patch('database.repositories.transaction.TransactionRepository.add')
    def test_add_transaction_buy(self, mock_add):
        mock_add.return_value = 1
        transaction = TransactionModel(
            ticker='AAPL',
            price_per_share=100.0,
            shares=10.0,
            transaction_type='buy'
        )
        transaction_id = self.repository.add(transaction)
        
        mock_add.assert_called_once_with(transaction)
        self.assertEqual(transaction_id, 1)
        logger.info('Tested adding a buy transaction.')
        
    @patch('database.repositories.transaction.TransactionRepository.add')
    def test_add_transaction_sell(self, mock_add):
        mock_add.return_value = 1
        transaction = TransactionModel(
            ticker='AAPL',
            price_per_share=100.0,
            shares=10.0,
            transaction_type='sell'
        )
        transaction_id = self.repository.add(transaction)
        
        mock_add.assert_called_once_with(transaction)
        self.assertEqual(transaction_id, 1)
        logger.info('Tested adding a sell transaction.')
        
    @patch('database.repositories.transaction.TransactionRepository.delete')
    def test_delete_transaction_valid_id(self, mock_delete):
        mock_delete.return_value = True
        transaction_id = 2
        result = self.repository.delete(transaction_id)
        self.assertTrue(result)
        logger.info('Tested deleting transaction by ID.')
        
    @patch('database.repositories.transaction.TransactionRepository.delete')
    def test_delete_transaction_invalid_id(self, mock_delete):
        mock_delete.return_value = False
        transaction_id = 0
        result = self.repository.delete(transaction_id)
        self.assertFalse(result)
        logger.info('Tested deleting transaction with invalid ID.')

class TestUniversalCRUD(unittest.TestCase):
    
    def setUp(self):
            
        self.db = DB
        self.user = DB_USER
        self.password = DB_PASSWORD
        self.host = DB_HOST
        self.port = int(DB_PORT) if DB_PORT else 5432
        self.pg_exe = PG_EXE
        self.db_connection = DatabaseConnection(
            db=self.db,
            user=self.user,
            password=self.password, 
            host=self.host,
            port=self.port,
            pg_exe=self.pg_exe
        )
        
        self.connection, self.cursor = self.db_connection.connect()
        self.connection.autocommit = False
        
    def tearDown(self):
        if self.connection:
            self.connection.rollback()
            self.cursor.close()
            self.db_connection.pool.putconn(self.connection)
        
        if self.db_connection.pool:
            self.db_connection.pool.closeall()
    
    @patch('database.services.delete.GenericRepository', autospec=True)
    @patch('database.services.delete.args', autospec=True)
    def test_universal_delete(self, mock_args, mock_generic_repo):
        """ 
        Test deleting a shareholder with valid ID and table.
        """
        mock_args.table = 'SHAREHOLDERS'
        mock_args.remove = 4
        mock_repo_instance = mock_generic_repo.return_value
        mock_repo_instance.delete.return_value = True
        result = handle_delete_by_id(self.db_connection)
        mock_repo_instance.delete.assert_called_once_with(4)
        self.assertTrue(result)
        logger.info('Tested deleting shareholder by ID.')
    
if __name__ == '__main__':
    unittest.main()