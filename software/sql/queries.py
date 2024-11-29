class Queries:
    """
    Class to store queries for interaction between the user, software and the database.
    """
    
    def __init__(self):
        pass
    
    ############################################################################
    ########################### General QUERIES ################################
    ############################################################################
    
    @staticmethod
    def FetchTableQuery(table_name: str):
        """
        SQL query for fetching table data from a given table.
        
        Args:
            table_name (str): The name of the given table. 
        """
        return f'SELECT * FROM {table_name}'
    
    @staticmethod
    def SelectFromTableQuery(table_name: str, condition_column: str = None):
        """
        Generalized SQL query for selecting rows from a table with an optional condition.
        """
        if condition_column:
            return f'SELECT * FROM {table_name} WHERE {condition_column} = %s'
        else:
            return f'SELECT * FROM {table_name}'
        
    @staticmethod
    def SelectColumnsFromTableQuery(table_name: str, columns: list, condition_column: str = None):
        """
        Generalized SQL query for selecting specific columns from a table with an optional condition.
        
        Args:
            table_name (str): The name of the table to selecty from.
            columns (list): The list of columns to select.
            condition_column (str, optional): The column for the WHERE condition.
        
        Returns: 
            str: The generated SQL query string.
        """
        columns_str = ', '.join(columns)
        if condition_column:
            return f'SELECT {columns_str} FROM {table_name} WHERE {condition_column}'
        return f'SELECT {columns_str} FROM {table_name}'
        
    @staticmethod
    def ConditionalUpdateTableQuery(table_name: str, columns: list, condition_column: str):
        """
        Generalized SQL query for updating a table's specific columns with a condition.
        """
        set_clause = ', '.join([f"{column} = %s" for column in columns])
        return f'UPDATE {table_name} SET {set_clause} WHERE {condition_column} = %s'

    @staticmethod
    def UpdateTableQuery(table_name, columns):
        """
        Generalized SQL query for updating a table's specific columns with a condition.

        Args:
            table_name (str): The name of the table to update.
            columns (list): The list of columns to update.

        Returns:
            str: The generated SQL query string.
        """
        set_clause = ', '.join([f"{column} = %s" for column in columns])
        return f"UPDATE {table_name} SET {set_clause} WHERE TICKER = %s"

    @staticmethod
    def InsertIntoTableQuery(table_name: str, columns: list):
        """
        Generalized SQL query for inserting data into a table.

        Args:
            table_name (str): The name of the table to insert into.
            columns (list): A list of column names where the data will be inserted.

        Returns:
            str: The generated SQL query string.
        """
        columns_str = ', '.join(columns)   
        placeholders = ','.join(['%s'] * len(columns))
        return f'INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders});'
    
    @staticmethod
    def DeleteFromTableQuery(table_name: str, condition_column: str):
        """ 
        Generalized SQL query for deleting a row from a table based on a condition.
        """
        return f'DELETE FROM {table_name} WHERE {condition_column} = %s'
    
    @staticmethod
    def TruncateTableData(table_name=None):
        """Truncate the table data"""
        
        if table_name == None:
            print(f'Database data truncated.')
            return 'TRUNCATE TABLE SHAREHOLDERS, FIRM, TRANSACTIONS, PORTFOLIO RESTART IDENTITY CASCADE;'
        elif table_name is not None:
            print(f'Database data truncated.')
            return f'TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;'
    
    ############################################################################
    ########################### SHAREHOLDER QUERIES ############################
    ############################################################################
    
    @staticmethod
    def AddShareholderQuery():
        """SQl query for adding a shareholder"""
        return """
            INSERT INTO SHAREHOLDERS (NAME, OWNERSHIP, INVESTMENT, EMAIL)
            VALUES (%s, %s, %s, %s);
        """
    
    ############################################################################
    ########################### TRANSACTION QUERIES ############################
    ############################################################################
    
    @staticmethod
    def TransactionQuery():
        """SQL query for a buy transaction query."""
        return """
            INSERT INTO TRANSACTIONS (FIRM_ID, TICKER, SHARES, PRICE_PER_SHARE, TRANSACTION_TYPE)
            VALUES (%s, %s, %s, %s, %s);
        """

    