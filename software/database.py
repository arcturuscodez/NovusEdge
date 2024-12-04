from sql import queries as q
from psycopg2 import OperationalError
import psycopg2 as psy  # PostgreSQL database adapter
import traceback
import utility
import subprocess
import time

class Database:
    """
    A class for the management and manipulation of the database.
    """
    
    def __init__(self, db, user, password, host, port):
        """
        Begin connection start.

        Args:
            db (str): The database to connect to.
            user (str): the username
            password (str): password
            host (str, optional): Host. Defaults to 'localhost'.
            port (int, optional): Port. Defaults to 5432.
        """
        self.db = db
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        
        self.connection = None
        self.cursor = None
    
    def start_server(self):
        """Start the PostgreSQL server."""
        try:
            print('Attempting to start PostgreSQL server...')
            command = r'"C:\Program Files\PostgreSQL\17\bin\pg_ctl.exe" start -D "C:\Program Files\PostgreSQL\17\data"'
            subprocess.run(command, check=True, shell=True)
            print('PostgreSQL server started.')
        except subprocess.CalledProcessError as e:
            print(f'Failed to start PostgreSQL server: {e}')
            raise
    
    def __enter__(self):
        """Open a connection to the database when entering the context."""
        attempt = 0
        while attempt < 3:
            try:
                self.connection = psy.connect(
                    host=self.host,
                    database=self.db,
                    user=self.user,
                    password=self.password,
                    port=self.port  
                )
                self.cursor = self.connection.cursor()
                print(f'Database connected at: {self.db}')
                return self
            
            except OperationalError as e:
                print(f"Error connecting to database: {e}")
                if "Connection refused" in str(e):
                    self.start_server()
                    time.sleep(5)
                else:
                    break
            attempt += 1
        raise Exception("Failed to connect to the database after multiple attempts.")
        
    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Close the connection to the database when exiting the context."""
        try:
            if exc_type:
                print(f'An error occurred: {exc_value}. Rolling back transaction.')
                self.connection.rollback()
                traceback.print_tb(exc_traceback)
            else:
                self.connection.commit()
            self.cursor.close()
            self.connection.close()
            print(f'Database connection closed at: {self.db}')
            
        except psy.DatabaseError as e:
            print(f'Error: {e}')
            raise e
        
    def __fetch__(self, table_name, print_data = False):
        """Fetches all data from a specified table, and optionally prints the data to the terminal or returns it."""
        try:
            self.cursor.execute(q.Queries.FetchTableQuery(table_name))
            columns = [description[0] for description in self.cursor.description]
            data = self.cursor.fetchall()
            if not data:
                print(f'No data to display.')
                return None
            if print_data:
                utility.FormatTableData(columns, data)
                return None
            
        except psy.DatabaseError as e:
            print(f'Error: {e}')
            traceback.print_exc()
            raise
        
    def __get__(self, table_name, column, print_data = False):
        """Get data from a specified table and column. Optionally print the data to the terminal or return it."""
        try:
            query = f'SELECT {column} FROM {table_name}'
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            if not data:
                print(f'No data to display for column {column}.')
                return None
            
            if print_data:
                utility.FormatTableData([column], data)
                return None
            
            return [row[0] for row in data]
        
        except psy.DatabaseError as e:
            print(f'Error: {e}')
            traceback.print_exc()
            raise
        
    def __log__(self, log_type: str, message: str): # Not functional
        """
        Logs an event in the HISTORY table.

        Args:
            log_type (str): The type of event ('INSERT', 'UPDATE', 'DELETE', etc.).
            message (str): A description or message related to the event.
        """
        try:
            self.cursor.execute()
            print(f'Logged event: {log_type} - {message}')
        
        except psy.DatabaseError as e:
            print(f'An error occured while trying to log the event: {e}')
            self.connection.rollback()
        
    def __update__(self, update_type, columns, values, condition_column=None, condition_value=None):
        """Updates any table and columns based on the provided arguments.
        
        Args:
            update_type (str): The type of update.
            columns (str): The columns to be updated.
            values (float): The value of the update.
            condition_column (str): The condition of the update.
            condition_value (flaot): The value of the condition.
        """
        try:
            print(f'Updating columns: {columns} with values: {values}')
            query, params = q.Queries.GeneralizedUpdateTableQuery('FIRM', columns, values, condition_column, condition_value)
            self.cursor.execute(query, tuple(params))
            print(f'Successfully updated {columns} with values {values}')
        except Exception as e:
            self.connection.rollback()
            print(f'Error occured updating the table: {e}')
        
class Shareholder(Database):
    
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor
        
    def shareholder_add(self, name: str, ownership: float, investment: float, email: str):
        """
        Adds a new shareholder to the SHAREHOLDERS table.

        Args:
            name (str): The name of the shareholder.
            ownership (float): The ownership of the investment firm the shareholder currently owns.
            investment (float): The total amount the shareholder has invested.
            date (str): The date the shareholder entered into the investment firm.
            email (str): The shareholders email address.
        """
        try:
            self.cursor.execute(q.Queries.InsertIntoTableQuery('SHAREHOLDERS', ['NAME', 'OWNERSHIP', 'INVESTMENT', 'EMAIL']), (name, ownership, investment, email))
            self.__update__('cash_reserve', ['CASH_RESERVE'], [investment])
            print(f'Shareholder {name} added successfully.')
            return True
        except psy.IntegrityError as e:
            self.connection.rollback()
            print(f'Error: A shareholder with email {email} already exists. Details: {e}')
        except psy.DatabaseError as e:
            print(f"Error: Could not add shareholder '{name}' to the SHAREHOLDERS table.")
            traceback.print_exc()
            return False
        
    def shareholder_remove(self, id: int):
        """
        Removes a shareholder by their ID from the SHAREHOLDERS table.

        Args:
            id (int): The ID of the shareholder to remove.
        """
        try:
            self.cursor.execute(q.Queries.SelectFromTableQuery('SHAREHOLDERS', 'ID'), (id,))
            shareholder = self.cursor.fetchone()
            if shareholder is None:
                print(f'No shareholder found with ID {id}.')
                return False
            self.cursor.execute(q.Queries.DeleteFromTableQuery('SHAREHOLDERS', 'ID'), (id,))
            print(f'Shareholder with ID {id} removed successfully.')
            return True
        except psy.DatabaseError as e:
            print(f'Error occured during the removal of shareholder with ID {id}: {e}')
            
    def shareholder_edit(self, input: str):
        """
        Edit an existing shareholder's details based on input string.

        Args:
            input (str): The input string in the format '<id> name=value ownership=value ...'
        """
        try:
            parts = input.split(' ', 1)
            id = int(parts[0])
            kwargs = {}
            
            if len(parts) > 1:
                for item in parts[1].split():
                    key, value = item.split('=')
                    kwargs[key] = value
                    
            if not kwargs:
                print('No fields provided for update.')
                return False
            
            self.cursor.execute(q.Queries.SelectFromTableQuery('SHAREHOLDERS', 'ID'), (id,))
            shareholder = self.cursor.fetchone()

            if not shareholder:
                print(f'No shareholder found with ID {id}')
                return False

            update_fields = []
            values = []

            for key, value in kwargs.items():
                update_fields.append(key.upper())
                values.append(value)

            if update_fields:
                values.append(id)
                self.cursor.execute(q.Queries.ConditionalUpdateTableQuery('SHAREHOLDERS', update_fields, 'ID'), tuple(values))
                self.connection.commit()
                print(f'Shareholder with ID {id} has been updated.')
            else:
                print('No fields provided for update.')

        except psy.DatabaseError as e:
            print(f'An error occurred while trying to update the shareholder: {e}')
            self.connection.rollback()
            return False
        
class Firm(Database):
    
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor
    
    def initialize_firm(self, firm_name):
        """Initialize the firm row in the FIRM table"""
        query = """
            INSERT INTO FIRM (FIRM_NAME, TOTAL_VALUE, TOTAL_VALUE_INVESTMENTS, CASH_RESERVE, NET_PROFIT, NET_LOSS)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """
        try:
            self.cursor.execute(query, (firm_name, 0, 0, 0, 0, 0))  # Initialize with default values
            self.connection.commit()
            print(f"Firm {firm_name} initialized successfully.")
        except Exception as e:
            self.connection.rollback()
            print(f"Error initializing firm: {e}")
            
class Transactions(Database):
    
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor
        
        self.firm_id = 1  # Default firm ID

    def transaction_buy(self, ticker: str, shares: int, pps: float):
        """
        Create a buy transaction.

        Args:
            ticker (str): The ticker of the stock purchased.
            shares (int): The number of shares of the ticker purchased.
            pps (float): The price per individual share purchased.
        """
        try:
            transaction_value = shares * pps # Calculate transaction value
            
            self.cursor.execute(q.Queries.InsertIntoTableQuery('TRANSACTIONS', ['FIRM_ID', 'TICKER', 'SHARES', 'PRICE_PER_SHARE', 'TRANSACTION_TYPE']), (self.firm_id, ticker, shares, pps, 'buy')) # Add transaction to the TRANSACTION table
            
            self.cursor.execute(
                """
                UPDATE FIRM
                SET CASH_RESERVE = CASH_RESERVE - %s
                """,
                (transaction_value,)
            )
            
            print(f'Buy transaction added: {shares} shares of {ticker} at {pps} per share.')
            
        except psy.DatabaseError as e:
            print(f'An error occured while creating the buy transaction: {e}')
            self.connection.rollback()
            return False
    
    def transaction_sell(self, ticker: str, shares: int, pps: float):
        """
        Create a sell transaction.
        
        Args:
            ticker (str): The ticker of the stock purchased.
            shares (int): The number of shares of the ticker purchased.
            pps (float): The price per individual share purchased.
        """
        try:
            transaction_value = shares * pps
            
            self.cursor.execute(q.Queries.InsertIntoTableQuery('TRANSACTIONS', ['FIRM_ID', 'TICKER', 'SHARES', 'PRICE_PER_SHARE', 'TRANSACTION_TYPE']), (self.firm_id, ticker, shares, pps, 'sell'))
            
            self.cursor.execute(
                """ 
                UPDATE FIRM
                SET CASH_RESERVE = CASH_RESERVE + %s
                """,
                (transaction_value,)
            )
            
            print(f'Sell transaction added: {shares} shares of {ticker} at {pps} per share.')
        
        except psy.DatabaseError as e:
            print(f'An error occured while creating the buy transaction: {e}')
            self.connection.rollback()
            return False
    
    def transaction_edit(self, id):
        pass
    
class History(Database):
    
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor
    
    def edit_history(self, id):
        pass
    
class Portfolio(Database):
    
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor

    def live_data(self):
        """
        Updates the columns of the PORTFOLIO table where live data is required,
        including current price, unrealized profit/loss, dividend yield percentage, 
        and dividend yield amount.

        The method fetches the required live data and updates the respective fields in the PORTFOLIO table.
        """
        from stocks import StocksManager
        daily_data = StocksManager()
        try:
            self.cursor.execute('SELECT TICKER FROM PORTFOLIO')
            tickers = self.cursor.fetchall()
            for stock in tickers:
                ticker = stock[0]
                current_price, latest_dividend = daily_data.DailyData(ticker)
                if current_price is not None and latest_dividend is not None:
                    self.cursor.execute(q.Queries.SelectColumnsFromTableQuery('PORTFOLIO', ['SHARES', 'AVERAGE_PURCHASE_PRICE'], 'TICKER = %s'), (ticker,))
                    shares, avg_price = self.cursor.fetchone()
                    unrealized_profit_loss = (shares * current_price) - (shares * avg_price)
                    if current_price > 0:
                        dividend_yield = latest_dividend / current_price
                    else:
                        dividend_yield = 0
                    dividend_yield_amt = (shares * current_price) * dividend_yield
                    self.cursor.execute(q.Queries.UpdateTableQuery('PORTFOLIO', [
                        'CURRENT_PRICE', 'UNREALIZED_PROFIT_LOSS', 'DIVIDEND_YIELD_PERCENTAGE', 'DIVIDEND_YIELD_AMOUNT'
                    ]), (
                        current_price, unrealized_profit_loss, 
                        dividend_yield, dividend_yield_amt, ticker
                    ))
                    #print(f'Updated live data for {ticker}: Current Price: {current_price}, Unrealized P/L: {unrealized_profit_loss}, Dividend Yield: {dividend_yield * 100}%, Dividend Yield Amount: {dividend_yield_amt}')
                else:
                    print(f'Live data unavailable for {ticker}. Skipping update.')
                    continue

        except psy.DatabaseError as e:
            self.connection.rollback()
            print(f'An error occurred while acquiring live data: {e}')