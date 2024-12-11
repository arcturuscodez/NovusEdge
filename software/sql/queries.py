class Queries:
    """A class to store queries for interaction between the user, software and the database."""
    
    def __init__(self):
        pass
    
    @staticmethod
    def FetchTableDataQuery(table_name: str, columns: list = None, condition_column: str = None):
        """
        Generalized SQL query for fetching table data from a given table, with optional columns and condition.

        Args:
            table_name (str): The name of the given table.
            columns (list, optional): The list of columns to select. If None, all columns are selected.
            condition_column (str, optional): The column for the WHERE condition. If None, no condition is applied.
            
        Returns:
            str: The generated SQL query string.
        """
        if columns:
            columns_str = ', '.join(columns)
            query = f'SELECT {columns_str} FROM {table_name}'
        else:
            query = f'SELECT * FROM {table_name}'
        if condition_column:
            query += f' WHERE {condition_column} = %s'
        
        return query
    
    @staticmethod
    def UpdateTableDataQuery(table_name: str, columns: list, values: list, condition_column: str = None, condition_value: any = None):
        """
        Generalized SQL query for updating a table with specific columns and optional conditions.

        Args:
            table_name (str): The name of the table to update.
            columns (list): List of columns to be updated.
            values (list): List of values corresponding to the columns.
            condition_column (str, optional): The column name to use for the WHERE condition.
            condition_value (any, optional): The value for the condition column to match rows.

        Returns:
            str: The generated SQL query string.
            list: The list of values to be used in the query (including condition value if present).
        """
        set_clause = ', '.join([f"{column} = %s" for column in columns])
        query = f'UPDATE {table_name} SET {set_clause}'
        
        if condition_column and condition_value is not None:
            query += f" WHERE {condition_column} = %s"
            return query, values + [condition_value]
        
        return query, values
    
    @staticmethod
    def InsertIntoTableQuery(table_name: str, columns: list, values: list = None):
        """ 
        Generalized SQL query for inserting data into a table.
        
        Args:
            table_name (str): The name of the table to insert into.
            columns (list): A list of column names where the data will be inserted.
            values (list, optional): A list of values to insert. If None, the placeholders are returned without actual values.
        
        Returns:
            str: The generated SQL query string.
            list: The list of values to be inserted (if provided).    
        """
        if not columns:
            raise ValueError("Columns must be provided for the insert query.")
        
        columns_str = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))
        query = f'INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})'
        
        return query, values if values else []
    
    @staticmethod
    def DeleteFromTableQuery(table_name: str, condition_column: str, condition_value: any = None):
        """ 
        Generalized SQL query for deleting a row from a table based on a condition.
        
        Args:
            table_name (str): The name of the table to delete from.
            condition_column (str): The column name to use for the WHERE condition.
            condition_value (any, optional): The value to match aganist the condition column.
        
        Returns:   
            str: The generated SQL query string.
            list: The list of values to be used with the query.    
        """
        if not condition_column:
            raise ValueError("A condition column must be provided for deletion.")
        
        query = f'DELETE FROM {table_name} WHERE {condition_column} = %s'
        return query, [condition_value] if condition_value else []
        
    @staticmethod
    def TruncateTableDataQuery(table_name=None):
        """Truncate the table data"""
        
        if table_name == None:
            print(f'Database data truncated.')
            return 'TRUNCATE TABLE SHAREHOLDERS, FIRM, TRANSACTIONS, PORTFOLIO RESTART IDENTITY CASCADE;'
        elif table_name is not None:
            print(f'Database data truncated.')
            return f'TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;'