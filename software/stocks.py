import yfinance as yf
import pandas as pd
import datetime as dt

class StocksManager:
    """Class for the management, collection, and analysis of stock data."""
    
    def __init__(self):
        pass
    
    @staticmethod
    def fetch_historical_data(ticker, period='1y'):
        """
        Fetch historical stock data for a given ticker.
        
        Args:
            ticker (str): Stock ticker.
            period (str): Period for historical data (e.g., '1y', '6mo')
            
        Returns:
            pd.DataFrame: Historical stock data.
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            print(f'Fetched historical data for {ticker}')
            return hist
        except Exception as e:
            print(f'Error fetching data for {ticker}: {e}')
            return pd.DataFrame()
        
    def fetch_testing_data(ticker = 'SPY', period = '1y'):
        """ 
        Fetch testing data for a given ticker.
        
        Args:
            ticker (str): Stock ticker.
            period (str): Period for historical data (e.g., '1y', '6mo')
            
        Returns:
            pd.DataFrame: Historical stock data.
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            return hist
        except Exception as e:
            print(f'Error fetching data for {ticker}: {e}')
            return pd.DataFrame()
    
    @staticmethod
    def download_stock_data(ticker):
        """ 
        Download stock data entirely.
        
        Args:
            ticker (str): Stock ticker.
            date (datetime): The date to start download from.
            
        Returns:
            N/A: For now 
        """
        try:
            start = pd.to_datetime('2004-08-01')
            data = yf.download(ticker, start=start, end=dt.date.today())
            if not data.empty:
                print(data)
                print(f'Downloaded stock data for {ticker}')
                return data
            else:
                print(data.head())
                print(f'Error downloading stock data.')
                raise
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
        
    @staticmethod
    def DailyData(ticker):
        """Acquire the daily data of a given stock"""
        stock = yf.Ticker(ticker)

        dividend_data = stock.dividends
        current_price = stock.history(period='1d')['Close'][0]
        
        if not dividend_data.empty:
            quarterly_latest_dividend_amount = dividend_data.iloc[-1]
            annual_latest_dividend_amount = quarterly_latest_dividend_amount * 4
            
            return current_price, annual_latest_dividend_amount
        else:
            print(f'No dividend data available for {ticker}')
            return None, None
        
    @staticmethod
    def CheckStock(ticker):
        """Check a stock to see if it exists in the yahoo finance module"""
        stock = yf.Ticker(str(ticker))
        info = stock.info
        
        if info:
            print(f'Stock: {stock} with ticker: {ticker} exists.')
        else:
            raise ValueError(f"Stock with ticker {ticker} not found.")