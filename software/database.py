from sql import queries as q
from psycopg2 import OperationalError
import psycopg2 as psy
import traceback
import utility
import subprocess
import time

class Database:
    """
    A class for the management and manipulation of the database.
    """
    
    def __init__(self, db: str, user: str, password: str, host: str, port: int, pg_exe: str, max_retries: int = 3, retry_delay: int = 5):
        """
        Initialize database connection arguments
        
        Args:
            db (str): The name of the database to connect to.
            user (str): Database username.
            password (str): Database password.
            host (str, optional): Host. Defaults to 'localhost'
            port (int, optional): Port. Defaults to 5432.
            pg_exe (str, optional): The command to start the PostgreSQL server.
            max_retries (int): Maximum number of connection retries.
            retry_delay (int): Delay between connection retries.
        """
        self.db = db
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self.connection = None
        self.cursor = None
        
        self.pg_exe = pg_exe
        
    def start_server(self):
        """Start the PostgreSQL server."""
        try:
            result = subprocess.run(
                ['pg_isready', '-h', self.host, '-p', str(self.port)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            if result.returncode == 0:
                print('PostgreSQL server is already running.')
                return
            
            print('Attempting to start PostgreSQL server...')
            subprocess.run(self.pg_exe, check=True, shell=True, timeout=60)
            print('PostgreSQL server started.')
        except subprocess.CalledProcessError as e:
            print(f'Failed to start PostgreSQL server: {e}')
            raise
        except subprocess.TimeoutExpired as e:
            print(f'Timed out trying to start PostgreSQL server: {e}')
            raise
    
    def connect(self):
        """Attempt to establish a database connection."""
        attempt = 0
        while attempt < self.max_retries:
            try:
                self.connection = psy.connect(
                    database = self.db,
                    user = self.user,
                    password = self.password,
                    host = self.host,
                    port = self.port
                )
                self.cursor = self.connection.cursor()
                print(f'Database connected at: {self.db}')
                return self
            except OperationalError as e:
                print(f'Error entering a connection to the database: {e}')
                if 'Connection refused' in str(e):
                    self.start_server()
                    time.sleep(self.retry_delay * (2 ** attempt))
                else:
                    break
            attempt += 1
        raise Exception('Failed to connect to the database after multiple attempts.')    
                
    def __enter__(self):
        """Enter a connection to the database when entering the context (Database)."""
        return self.connect()
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Close the connection to the database when exiting the context (Database)."""
        try:
            if exc_type:
                print(f'An error occurred: {exc_value}. Rolling back transaction.')
                self.connection.rollback()
                traceback.print_tb(exc_traceback)
            else:
                self.connection.commit()
        except psy.DatabaseError as e:
            print(f'Database error: {e}')
            raise e
        finally:
            try:
                self.cursor.close()
                self.connection.close()
                print(f'Database connection closed at: {self.db}')
            except (AttributeError, psy.DatabaseError) as e:
                print(f'Error closing database connection: {e}')
                
    def fetch_data(self, table_name: str, columns: list = None, condition: str = None, condition_value: any = None, print_data: bool = False):
        """ 
        Fetch data from a specified table with optional columns, condition, and printing.
        
        Args:
            table_name (str): Name of the table to fetch data from.
            columns (list, optional): List of columns to fetch. Fetches all columns if None.
            condition (str, optional): Column name for the WHERE condition.
            condition_value (any, optional): Value for the WHERE condition.
            print_data (bool, optional): Whether to print the fetched data. Default is False.
            
        Returns:
            List: List of fetched rows. Returns None if print_data is True or no data is found.
        """
        try:
            query = q.Queries.FetchTableDataQuery(table_name, columns, condition)
            if condition and condition_value is not None:
                self.cursor.execute(query, (condition_value,))
            else:
                self.cursor.execute(query)
                
            data = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
            
            if not data:
                print(f'No data to display from {table_name}')
                return None
            
            if print_data:
                utility.FormatTableData(columns, data)
                return None
            
            return data
        
        except psy.errors.UndefinedTable as e:
            print(f'A database error occurred when fetching data: {e}')
        except psy.DatabaseError as e:
            print(f'A database error occurred when fetching data: {e}')
        except ValueError as e:
            print(f'Value error: {e}')
        except Exception as e:
            print(f'An unexpected error occured: {e}')
        finally:
            self.connection.rollback()
        
    def update_table(self, table_name: str, columns: list, values: list, condition_column: str = None, condition_value: any = None):
        """
        Updates specified columns in a table based on the provided arguments.

        Args:
            table_name (str): The name of the table to update.
            columns (list): List of columns to update.
            values (list): List of values corresponding to the columns.
            condition_column (str, optional): The column to use as the WHERE condition. Defaults to None.
            condition_value (any, optional): The value for the condition column. Defaults to None.

        Returns:
            None
        """
        try:
            print(f'Updating table: {table_name}, Columns: {columns}, Values: {values}, Condition: {condition_column} = {condition_value}')
            query, params = q.Queries.UpdateTableDataQuery(table_name, columns, values, condition_column, condition_value)
            
            self.cursor.execute(query, tuple(params))
            print(f"Successfully updated {table_name}: {columns} with {values}")
            
        except Exception as e:
            self.connection.rollback()
            print(f'Error occurred while updating the table: {e}')
            traceback.print_exc()
            raise
        
class Shareholder(Database):
    
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor
        
    def shareholder_add(self, name: str, ownership: float, investment: float, email: str):
        """ 
        Adds a new shareholder to the SHAREHOLDERS table.
        
        Args:
            name (str): The name of the shareholder.
            ownership (float): Ownership percentage of the firm.
            investment (float): The total amount the shareholder has invested.
            email (str): The shareholder's email_address.
        """
        try:
            query, params = q.Queries.InsertIntoTableQuery(
                'SHAREHOLDERS',
                ['NAME', 'OWNERSHIP', 'INVESTMENT', 'EMAIL'],
                [name, ownership, investment, email]
            )
            self.cursor.execute(query, params)
            
            query = "UPDATE FIRM SET CASH_RESERVE = CASH_RESERVE + %s"
            params = [investment]
            self.cursor.execute(query, params)
            
            print(f'Shareholder {name} added successfully.')
            return True
        except psy.IntegrityError as e:
            self.connection.rollback()
            print(f'Error: A shareholder with email {email} already exists. Details: {e}')
        except psy.DatabaseError as e:
            self.connection.rollback()
            print(f"Error: Could not add shareholder '{name}'. Details: {e}")
            traceback.print_exc()
        return False
    
    def shareholder_remove(self, shareholder_id: int):
        """ 
        Removes a shareholder by their ID from the SHAREHOLDERS table.
        
        Args:
            shareholder_id (int): The ID of the shareholder to remove.
        """
        try:
            query = q.Queries.FetchTableDataQuery('SHAREHOLDERS', condition_column='ID')
            self.cursor.execute(query, (shareholder_id,))
            shareholder = self.cursor.fetchone()
            
            if not shareholder:
                print(f'No shareholder found with ID {shareholder_id}')
                return False
            
            delete_query, params = q.Queries.DeleteFromTableQuery('SHAREHOLDERS', 'ID', shareholder_id)
            self.cursor.execute(delete_query, params)
            print(f'Shareholder with ID {shareholder_id} removed successfully.')
            return True
        except psy.DatabaseError as e:
            self.connection.rollback()
            print(f'Error occurred during the removal of shareholder ID {shareholder_id}: {e}')
        return False
    
    def shareholder_edit(self, input_str: str):
        """ 
        Edits an existing shareholder's details based on the input string.
        
        Args:
            input_str (str): The input string in the format '<id> name=value ownership=value ...'.
        """
        try:
            parts = input_str.split(' ', 1)
            shareholder_id = int(parts[0])
            if len(parts) < 2:
                print('No fields provided for update.')
                return False
            
            fields = parts[1].split()
            updates = {}
            for field in fields:
                key, value = field.split('=')
                updates[key.upper()] = value
                
            if not updates:
                print('No valid fields to update')
                return False
            
            query = q.Queries.FetchTableDataQuery('SHAREHOLDERS', condition_column='ID')
            self.cursor.execute(query, (shareholder_id,))
            if not self.cursor.fetchall():
                print(f'No shareholder found with ID {shareholder_id}')
                return False
            
            query, params = q.Queries.UpdateTableDataQuery('SHAREHOLDERS', list(updates.keys()), 'ID', shareholder_id)
            self.cursor.execute(query, params)
            print(f'Shareholder with ID {shareholder_id} has been updated.')
            return True
        except ValueError:
            print(f"Invalid input format. Please use '<id> key=value ...'.")
        except psy.DatabaseError as e:
            self.connection.rollback()
            print(f'An error occured while updating the shareholder: {e}')
        return False
    
    def shareholder_get(self):
        """
        Retrieves all shareholders from the SHAREHOLDERS table.
        
        Returns:
            list: A list of shareholder records.
        """
        try:
            query = q.Queries.FetchTableDataQuery('SHAREHOLDERS')
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            return data if data else []
        except psy.DatabaseError as e:
            print(f'Error fetching shareholders: {e}')
            return []

class Firm(Database):
    
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor
        
    def create_firm_rows(self, firm_name):
        """
        Initialize the static rows in the FIRM table.
        
        Args:
            firm_name (str): Name of the firm to create rows for.
        """
        create_firm_rows_query = """
            INSERT INTO FIRM (FIRM_NAME, TOTAL_VALUE, TOTAL_VALUE_INVESTMENTS, CASH_RESERVE, NET_PROFIT, NET_LOSS)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """
        try:
            self.cursor.execute(create_firm_rows_query, (firm_name, 0, 0, 0, 0, 0))
            print(f'Firm {firm_name} table rows initialized successfully.')
        except Exception as e:
            self.connection.rollback()
            print(f'Error initializing rows in the firm table: {e}')
        
    def update_total_investments(self):
        """ 
        Update the TOTAL_VALUE_INVESTMENTS column in the FIRM table.
        by summing up the TOTAL_VALUE from the portfolio table.
        """
        try:
            self.cursor.execute(
                """ 
                UPDATE FIRM
                SET TOTAL_VALUE_INVESTMENTS = (
                    SELECT COALESCE(SUM(TOTAL_VALUE), 0)
                    FROM PORTFOLIO
                    WHERE PORTFOLIO.FIRM_ID = FIRM.ID
                    )
                """
            )
        except psy.DatabaseError as e:
            print(f'An error occured while updating TOTAL_VALUE_INVESTMENTS: {e}')
            self.connection.rollback()
            
    def update_firm_total_value(self, firm_id: int = 1):
        """ 
        Updates the TOTAL_VALUE column in the FIRM table for the given firm_id.
        
        Args:
            firm_id (int): The ID of the firm to update.
        """
        try:
            self.cursor.execute(
                """ 
                SELECT TOTAL_VALUE_INVESTMENTS, CASH_RESERVE
                FROM FIRM
                WHERE ID = %s
                """,
                (firm_id,))
            result = self.cursor.fetchone()
            
            if result:
                total_value_investments, cash_reserve = result
                total_value = total_value_investments + cash_reserve
                
                self.cursor.execute(
                    """ 
                    UPDATE FIRM
                    SET TOTAL_VALUE = %s
                    WHERE ID = %s
                    """,
                    (total_value, firm_id))
            else:
                print(f'No firm found with ID {firm_id}')
                
        except Exception as e:
            print(f'An error occurred while updating TOTAL_VALUE: {e}')
            
class Transactions(Database):
    
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor
        
    def transaction_buy(self, ticker: str, shares: int, pps: float, firm_id: int = 1):
        """
        Create a buy transaction.

        Args:
            ticker (str): The ticker of the stock purchased.
            shares (int): The number of shares of the ticker purchased.
            pps (float): The price per individual share purchased.
            firm_id (int, optional): The id of the firm to insert transactions for.
        """
        try:
            transaction_value = shares * pps
            
            insert_query, params = q.Queries.InsertIntoTableQuery('TRANSACTIONS',
                                                                  ['FIRM_ID', 'TICKER', 'SHARES', 'PRICE_PER_SHARE', 'TRANSACTION_TYPE'],
                                                                  (firm_id, ticker, shares, pps, 'buy'))
            self.cursor.execute(insert_query, params)
            
            self.cursor.execute(
                """ 
                UPDATE FIRM
                SET CASH_RESERVE = CASH_RESERVE - %s
                """,
                (transaction_value,)
            )
            
            print(f'Buy transaction added: {shares} shares of {ticker} at {pps} per share.')
            self.connection.commit()
        
        except psy.DatabaseError as e:
            print(f'An error occurred while creating the buy transaction: {e}')
            self.connection.rollback()
            return False
    
    def transaction_sell(self, ticker: str, shares: int, pps: float, firm_id: int = 1):
        """ 
        Create a sell transaction.
        
        Args:
            ticker (str): The ticker of the stock purchased.
            shares (int): The number of shares of the ticker purchased.
            pps (float): The price per individual share purchased.
            firm_id (int, optional): The id of the firm to insert transactions for.
        """
        try:
            transaction_value = shares * pps
            
            insert_query, params = q.Queries.InsertIntoTableQuery('TRANSACTIONS',
                                                          ['FIRM_ID', 'TICKER', 'SHARES', 'PRICE_PER_SHARE', 'TRANSACTION_TYPE'],
                                                          (firm_id, ticker, shares, pps, 'sell'))  
            self.cursor.execute(insert_query, params)
            
            self.cursor.execute(
                """ 
                UPDATE FIRM
                SET CASH_RESERVE = CASH_RESERVE + %s
                """,
                (transaction_value,)
            )
            
            print(f'Sell transaction added: {shares} shares of {ticker} at {pps} per share.')
            self.connection.commit()
            
        except psy.DatabaseError as e:
            print(f'An error occurred while creating the buy transaction: {e}')
            self.connection.rollback()
            return False
            
    def transaction_edit(self):
        pass
    
    def transaction_get(self):
        pass
    
    def transaction_calculate(self):
        pass
    
class History(Database):
    
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor
        
    def history_edit(self):
        pass
    
    def history_get(self):
        pass
    
class Portfolio(Database):
    
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor
        
        from stocks import StocksManager
        self.daily_data = StocksManager()
        
    def portfolio_live_data(self):
        """
        Updates the columns of the PORTFOLIO table with live data: current price, 
        unrealized profit/loss, dividend yield percentage, and dividend yield amount.
        """
        from stocks import StocksManager
        update_data = StocksManager()
        try:
            tickers = self._get_all_tickers()
            for ticker in tickers:
                stock_data = self._fetch_stock_data(self.daily_data, ticker)
                if stock_data:
                    self._update_portfolio_row(ticker, *stock_data)
                else:
                    print(f'Live data unavailable for {ticker}. Skipping update.')
        except Exception as e:
            self.connection.rollback()
            print(f'An error occurred while updating live data: {e}')
    
    def portfolio_add(self):
        pass
    
    def portfolio_remove(self):
        pass
    
    def portfolio_edit(self):
        pass
    
    def _get_all_tickers(self):
        """Fetches all stock tickers from the PORTFOLIO table.
        
        Returns:
            list: A list of stock tickers.
        """
        data = self.fetch_data('PORTFOLIO', columns=['TICKER'])
        return [row[0] for row in data] if data else []
    
    def _fetch_stock_data(self, daily_data, ticker):
        """ 
        Fetches the live stock data for a given ticker.
        
        Args:
            daily_data (StocksManager): The stocks manager for fetching live data.
            ticker (str): The stock ticker symbol
            
        Returns:
            tuple: (currewnt_price, latest_dividend) if data is available, None otherwise.
        """
        try:
            current_price, latest_dividend = self.daily_data.DailyData(ticker)
            return (current_price, latest_dividend) if current_price and latest_dividend else None
        except Exception as e:
            print(f'Failed to fetch stock data for {ticker}: {e}')
            return None
        
    def _get_portfolio_row(self, ticker):
        """ 
        Fetches the portfolio row data (shares and average purchase price) for a ticker.
        
        Args:
            ticker (str): The stock ticker.
            
        Returns:
            tuple: (shares, average_purchase_price) or None if no data is found.
        """
        data = self.fetch_data('PORTFOLIO', columns=['SHARES', 'AVERAGE_PURCHASE_PRICE'], condition='TICKER', condition_value=ticker)
        return data[0] if data else None
    
    def _calculate_portfolio_metrics(self, shares, avg_price, current_price, latest_dividend):
        """
        Calculates unrealized profit/loss, dividend yield percentage, and dividend yield amount.

        Args:
            shares (int): Number of shares owned.
            avg_price (float): Average purchase price of the shares.
            current_price (float): Current market price of the stock.
            latest_dividend (float): Latest dividend amount.

        Returns:
            tuple: (unrealized_profit_loss, dividend_yield, dividend_yield_amount)
        """
        unrealized_profit_loss = (shares * current_price) - (shares * avg_price)
        dividend_yield = latest_dividend / current_price if current_price > 0 else 0
        dividend_yield_amount = (shares * current_price) * dividend_yield
        return unrealized_profit_loss, dividend_yield, dividend_yield_amount
    
    def _update_portfolio_row(self, ticker, current_price, latest_dividend):
        """ 
        Updates the PORTFOLIO table with live data metrics for a ticker.

        Args:
            ticker (str): The stock ticker.
            current_price (float): Current market price.
            latest_dividend (float): Latest dividend amount.
        """
        row = self._get_portfolio_row(ticker)
        if not row:
            print(f'No portfolio row found for ticker {ticker}. Skipping update.')
            return

        shares, avg_price = row
        unrealized_profit_loss, dividend_yield, dividend_yield_amount = self._calculate_portfolio_metrics(
            shares, avg_price, current_price, latest_dividend
        )

        try:
            query, params = q.Queries.UpdateTableDataQuery(
                'PORTFOLIO',
                ['CURRENT_PRICE', 'UNREALIZED_PROFIT_LOSS', 'DIVIDEND_YIELD_PERCENTAGE', 'DIVIDEND_YIELD_AMOUNT'],
                [current_price, unrealized_profit_loss, dividend_yield, dividend_yield_amount],
                condition_column='TICKER',
                condition_value=ticker
            )
            self.cursor.execute(query, params)
        except Exception as e:
            print(f'Error occurred updating portfolio row for {ticker}: {e}')
