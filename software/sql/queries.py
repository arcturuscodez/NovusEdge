class Queries:
    """
    Class to store queries for interaction between the user, software and the database.
    """
    
    def __init__(self):
        pass

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
        
    @staticmethod # Redundant
    def ConditionalUpdateTableQuery(table_name: str, columns: list, condition_column: str):
        """
        Generalized SQL query for updating a table's specific columns with a condition.
        """
        set_clause = ', '.join([f"{column} = %s" for column in columns])
        return f'UPDATE {table_name} SET {set_clause} WHERE {condition_column} = %s'

    @staticmethod
    def UpdateTableQuery(table_name, columns): # Redundant
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
    def GeneralizedUpdateTableQuery(table_name: str, columns: list, values: list, condition_column: str = None, condition_value: any = None):
        """
        Generalized SQL query for updating any table with any number of columns and values.

        Args:
            table_name (str): The name of the table to update.
            columns (list): List of columns to be updated.
            values (list): List of values corresponding to the columns.
            condition_column (str): Optional column name to use for the WHERE condition.
            condition_value (any): Optional value for the condition column to match rows.

        Returns:
            str: The SQL query string.
        """
        set_clause = ', '.join([f"{column} = %s" for column in columns])
        query = f'UPDATE {table_name} SET {set_clause}'
        if condition_column and condition_value is not None:
            query += f" WHERE {condition_column} = %s"
            return query, values + [condition_value]
        
        return query, values

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