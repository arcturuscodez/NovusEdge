from typing import Optional
from decimal import Decimal
from datetime import datetime, timedelta
import pytz
import threading
import time
import pandas as pd
import yfinance as yf

import logging

logger = logging.getLogger(__name__)

class Oracle:
    """Oracle class for fetching asset data."""
    _cache = {}
    _cache_lock = threading.Lock()

    def __init__(self, ticker: str, retries: int = 3, delay: int = 5):
        """
        Initialize the Oracle class.

        Args:
            ticker (str): The asset ticker.
            retries (int, optional): The number of retries fetching data. Defaults to 3.
            delay (int, optional): The delay between retries. Defaults to 5.
        """
        self.ticker = ticker
        self.retries = retries
        self.delay = delay

    def _validate_ticker(self, ticker: str = None) -> bool:
        """Validate the asset ticker."""
        if not isinstance(self.ticker, str) or not self.ticker:
            logger.error(f'Invalid ticker symbol provided: {self.ticker}')
            return False
        
        valid_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-")
        if not all(c.upper() in valid_chars for c in self.ticker):
            logger.error(f'Invalid ticker symbol provided: {self.ticker}')
            return False
        
        return True
        
    def _validate_dividends(self, dividends: Decimal = None) -> bool:
        """Validate if the most recent dividend is available, and if it was within the last year."""
        if dividends.empty:
            logger.info(f'No dividend data available for {self.ticker}')
            return False
        
        latest_dividend_date = dividends.index[-1].to_pydatetime()
        current_date = datetime.now(pytz.UTC)
        one_year_ago = current_date - timedelta(days=365)
        
        if latest_dividend_date < one_year_ago:
            logger.info(f'Latest dividend for {self.ticker} was on {latest_dividend_date}, over a year ago')
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
        if not self._validate_ticker():
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
        if not self._validate_ticker():
            return None
        
        try:
            logger.debug(f'Fetching latest closing price for {self.ticker}')
            ticker_data = yf.Ticker(self.ticker)
            hist = ticker_data.history(period='1d')
            if hist.empty:
                logger.warning(f'No recent data available for {self.ticker}')
                return None
            latest_close = hist['Close'].iloc[-1]
            logger.debug(f'Latest closing price for {self.ticker}: {latest_close}')
            return latest_close
        
        except Exception as e:
            logger.error(f'Failed to retrieve latest closing price for {self.ticker}: {e}')
            return None
        
    def get_sector(self) -> Optional[str]:
        """
        Retrieve the sector of the asset

        Returns:
            Optional[str]: The sector of the asset, or None if retrieval failed.
        """
        if not self._validate_ticker():
            return None
        
        try:
            logger.debug(f'Fetching sector for {self.ticker}')
            ticker_data = yf.Ticker(self.ticker)
            info = ticker_data.info
            if 'sector' in info:
                sector = info['sector']
                logger.debug(f'Sector for {self.ticker}: {sector}')
                return sector
            else:
                logger.info(f'No sector information available for {self.ticker}')
                return None
            
        except Exception as e:
            logger.error(f'Failed to retrieve sector for {self.ticker}: {e}')
            return None
        
    def get_dividend_yield(self) -> Optional[Decimal]:
        """
        Retrieve the current annual yield for the asset as a decimal value.
        
        Returns:
            Optional[Decimal]: The dividend yield as a decimal (e.g., 0.03 for 3%), or None if not available.
        """
        cache_key = f"{self.ticker}_dividend_yield"
        with self._cache_lock:
            if cache_key in self._cache:
                return self._cache[cache_key]

        if not self._validate_ticker():
            return None
        try:
            logger.debug(f'Fetching dividend yield for {self.ticker}')
            ticker_data = yf.Ticker(self.ticker)
            
            dividends = ticker_data.dividends
            if not self._validate_dividends(dividends):
                return Decimal('0')
            
            info = ticker_data.info
            if 'dividendYield' in info:
                yield_value = info['dividendYield']
                logger.debug(f'Dividend yield for {self.ticker}: {yield_value}')
                decimal_yield = Decimal(str(yield_value)) / Decimal('100') # Convert from percentage to decimal (e.g., 3% to 0.03)
                return decimal_yield # Return as a decimal value not a percentage value (e.g., 0.03)
            else:
                logger.info(f'No current or recent dividend yield available for {self.ticker}, but dividends exist')
                return Decimal('0')
            
        except Exception as e:
            logger.error(f'Failed to retrieve dividend yield for {self.ticker}: {e}')
            return None
        
    def custom_dividend_yield(self, div_yield: Decimal) -> Optional[Decimal]:
        """
        Calculate a custom dividend yield based on a user-provided value.

        Args:
            div_yield (Decimal): The custom dividend yield to use.

        Returns:
            Optional[Decimal]: The custom dividend yield as a decimal, or None if invalid.
        """
        if not isinstance(div_yield, Decimal):
            logger.error('Invalid dividend yield provided, must be a Decimal')
            return None
        
        if div_yield < Decimal('0'):
            logger.error('Invalid dividend yield provided, must be a positive value')
            return None
        
        return div_yield
    
    def get_additional_info(self) -> Optional[dict]:
        """
        Retrieve additional information for the asset, such as splits and actions.

        Returns:
            Optional[dict]: A dictionary containing additional information, or None if retrieval failed.
        """
        if not self._validate_ticker():
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