import numpy as np
import pandas as pd
import yfinance as yf

import logging 

logger = logging.getLogger(__name__)

from retriever import AssetRetriever

class DataProcessor:
    """Data processing class for asset data."""
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize the DataProcessor with a DataFrame.
        
        Args:
            data (pd.DataFrame): The asset data to process.
        """
        if not isinstance(data, pd.DataFrame):
            logger.error('Data must be a pandas DataFrame.')
            raise ValueError('Invalid data type.')
        self.data = data
        
    def inspect_data(self, n: int = 5) -> pd.DataFrame:
        """ 
        Inspect the first n rows of the data.
        
        Args:
            n (int): The number of rows to inspect.
        
        Returns: 
            pd.DataFrame: The first n rows of the data.
        """
        logger.debug(f'Inspecting the first {n} rows of the data.')
        return self.data.head(n)
    
    def process_data(self, column: str) -> pd.Series:
        """ 
        Process the data in the specified column by calculating daily returns.
        
        Args:
            column (str): The column to process.
           
        Returns: 
            pd.Series: The daily returns of the specified column
        """
        if column not in self.data.columns:
            logger.error(f'Column {column} not found in data.')
            raise KeyError(f'Column "{column}" not found.')
        
        logger.error(f'Calculating daily returns for column: {column}')
        returns = self.data[column].pct_change().dropna()
        return returns
    
    def clean_data(self) -> pd.DataFrame:
        """ 
        Clean the data by handling missing values.
        
        Returns:
            pd.DataFrame: The cleaned data.
        """
        logger.info('Cleaning data by filling missing values.')
        self.data.fillna(method='ffill', inplace=True)
        self.data.dropna(inplace=True)
        return self.data

    def add_moving_average(self, column: str, window: int = 20) -> pd.DataFrame:
        """ 
        Add a moving average column to the data.
        
        Args:
            column (str): The column to calculate the moving average for.
            window (int): The window size for the moving average.
        
        Returns:
            pd.DataFrame: The data with the moving average column added.
        """
        if column not in self.data.columns:
            logger.error(f'Column "{column}" does not exist in data.')
            raise KeyError(f'Column "{column}" not found.')
        
        ma_column = f'{column}_MA_{window}'
        logger.info(f'Adding moving average column: {ma_column}')
        self.data[ma_column] = self.data[column].rolling(window=window).mean()
        return self.data