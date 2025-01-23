import time
import numpy as np
import pandas as pd
import yfinance as yf

import logging 

logger = logging.getLogger(__name__)

from typing import Optional

class AssetRetriever:
    """A class for the retrieval of asset data using the Yahoo Finance API."""
    
    def __init__(self, ticker: str, retries: int = 3, delay: int = 5):
        """ 
        Initialize the AssetRetriever with a ticker symbol.
        
        Args:
            ticker (str): The ticker symbol of the asset.
            retries (int): The number of retries for fetching data.
            delay (int): The delay between retries.
        """
        self.ticker = ticker
        self.retries = retries
        self.delay = delay
        
    def validate_ticker(self) -> bool:
        """Validate the ticker symbol format."""
        if not isinstance(self.ticker, str) or not self.ticker.isalnum():
            logger.error(f'Invalid ticker symbol: {self.ticker}')
            return False
        return True
    
    def get_asset_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """ 
        Retrieve asset data for a given date range.
        
        Args:
            start_date (str): The start date of the data.
            end_date (str): The end date of the data.
        
        Returns: 
            pd.DataFrame: A DataFrame containg the asset data.
        """
        if not self.validate_ticker():
            return pd.DataFrame()
        
        attempt = 0
        
        while attempt < self.retries:
            
            try:
                logger.info(f'Fetching data for {self.ticker} from {start_date} to {end_date}')
                data = yf.download(self.ticker, start=start_date, end=end_date)
                if not data.empty:
                    logger.info(f'Data retrieval successful for {self.ticker}')
                    return data.reset_index()
                else:
                    logger.warning(f'No data found for {self.ticker}')
                    
            except yf.YFinanceError as e:
                logger.error(f'YFinance error occurred: {e}. Attempt {attempt + 1}')
            except Exception as e:
                logger.error(f'An error occurred fetching data: {e}. Attempt {attempt + 1}')
            attempt += 1
            time.sleep(self.delay)
        
        logger.error(f'Failed to retrieve data for {self.ticker} after {self.retries} attempts.')
        return pd.DataFrame()
    
    def get_latest_closing_price(self) -> Optional[float]:
        """ 
        Retrieve the latest closing price of the asset.
        
        Returns:
            Optional[float]: The latest closing price, or None if retrieval failed.
        """
        if not self.validate_ticker():
            return None
        
        try:
            logger.info(f'Fetching latest closing price for {self.ticker}')
            ticker_data = yf.Ticker(self.ticker)
            hist = ticker_data.history(period='1d')
            if hist.empty:
                logger.warning(f'No recent data available for {self.ticker}')
                return None
            latest_close = hist['Close'].iloc[-1]
            logger.info(f'Latest closing price for {self.ticker}: {latest_close}')
            return latest_close
        
        except Exception as e:
            logger.error(f'Failed to retrieve latest closing price for {self.ticker}: {e}')
            return None
        
    def get_dividend_info(self) -> Optional[pd.DataFrame]:
        """ 
        Retrieve dividend information for the asset.
        
        Returns:
            Optional[pd.DataFrame]: A DataFrame containing dividend information, or None if retrieval failed.
        """
        if not self.validate_ticker():
            return None
        
        try:
            logger.info(f'Fetching dividend information for {self.ticker}')
            ticker_data = yf.Ticker(self.ticker)
            dividends = ticker_data.dividends
            if dividends.empty:
                logger.info(f'No dividend information found for {self.ticker}')
                return pd.DataFrame()
            logger.info(f'Dividend information retrieved for {self.ticker}')
            return dividends.reset_index()

        except Exception as e:
            logger.error(f'Failed to retrieve dividend information for {self.ticker}: {e}')
            return None
        
    def get_additional_info(self) -> Optional[dict]:
        """
        Retrieve additional information for the asset, such as splits and actions.

        Returns:
            Optional[dict]: A dictionary containing additional information, or None if retrieval failed.
        """
        if not self.validate_ticker():
            return None
        
        try:
            logger.info(f'Fetching additional information for {self.ticker}')
            ticker_data = yf.Ticker(self.ticker)
            info = ticker_data.info
            splits = ticker_data.splits
            actions = ticker_data.actions
            additional_info = {
                'info': info,
                'splits': splits.reset_index() if not splits.empty else pd.DataFrame(),
                'actions': actions.reset_index() if not actions.empty else pd.DataFrame()
            }
            logger.info(f'Additional information for {self.ticker} retrieved successfully')
            return additional_info
        except Exception as e:
            logger.error(f'Failed to fetch additional information for {self.ticker}: {e}')
            return None
        