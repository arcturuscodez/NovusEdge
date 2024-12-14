import os 
import random
import numpy as np
import pandas as pd
import yfinance as yf

from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
from icarus.training import Training

class StocksDataFetcher:
    """
    Service to fetch stock data from external sources. (e.g. Yahoo Finance)
    This class provides methods to fetch stock data and dividend information for a given ticker quickly.
    """
    
    @staticmethod
    def fetch_stock_data(ticker):
        """ 
        Acquire the latest stock data for the given ticker.
        
        Args:
            ticker (str): The stock ticker symbol (e.g, 'AAPL', 'GOOG')
            
        Returns:
            tuple: The current stock price and the most recent QUARTERLY dividend amount (if available).
            If no dividend information is available, returns (current_price, None).
        """
        stock = yf.Ticker(ticker)
        dividend_data = stock.dividends
        current_price = float(stock.history(period='1d')['Close'].iloc[0])
        
        if not dividend_data.empty:
            quarterly_latest_dividend_amount = float(dividend_data.iloc[-1])
            return current_price, quarterly_latest_dividend_amount
        else:
            print(f'No dividend information available for {ticker}.')
            return current_price, None

class StockDataProcessor:
    """Class for the processing, management and transformation of stock data."""
    
    def __init__(self, ticker, model_type='random_forest'):
        """
        Initialize the StockDataProcessor instance.
        
        Args:
            ticker (str): The stock ticker symbol (e.g, 'AAPL', 'GOOG')
        """
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)
        self.training = Training(model_type=model_type)
        
    def get_basic_info(self):
        """ 
        Fetches basic stock information such as company name, sector, and website.
        
        Returns:
            dict: A dictionary containing basic stock information.
        """
        try:
            info = self.stock.info
            return {
                "short_name": info.get('shortName', 'N/A'),
                "currency": info.get('currency', 'N/A'),
                "sector": info.get('sector', 'N/A'),
                "industry": info.get('industry', 'N/A'),
                "website": info.get('website', 'N/A')
            }
        except Exception as e:
            print(f'Error fetching basic information: {e}')
            return {}
        
    def get_dividend_info(self):
        """
        Fetches dividend related information, including the most recent dividend and the annualized dividend.
        
        Returns:
            dict: A dictionary containing dividend information or indicating that the stock has no dividends.
        """
        try:
            dividends = self.stock.dividends
            if dividends.empty:
                return {"has_dividends": False}
            
            last_dividend = dividends.iloc[-1]
            return {
                "has_dividends": True,
                "last_dividend_date": dividends.index[-1],
                "last_dividend_amount": last_dividend,
                "annualized_dividend": last_dividend * 4 # Assuming quarterly dividends
            }
        except Exception as e:
            print(f'Error fetching dividend info: {e}')
            return {"has_dividends": False}
        
    def fetch_historical_data(self, start_date, end_date):
        """
        Fetches historical stock data between specified start and end dates.
        
        Args:
            start_date (str): The start date for the historical data (YYYY-MM-DD).
            end_date (str): The end date for the historical data (YYYY-MM-DD).
        
        Returns:
            pd.DataFrame: A DataFrame containing the historical stock data.
        """
        try:
            data = yf.download(self.ticker, start=start_date, end=end_date)
            print(f'Fetched historical data for {self.ticker}')
            return data
        except Exception as e:
            print(f'Error fetching historical data: {e}')
            return pd.DataFrame()
        
    def download_and_save_data(self, start_date, end_date, output_path):
        """
        Downloads historical stock data and saves it as a CSV file.
        
        Args:
            start_date (str): The start date for the historical data (YYYY-MM-DD).
            end_date (str): The end date for the historical data (YYYY-MM-DD).
            output_path (str): The directory path where the CSV file will be saved.
        
        Returns:
            str: The file path of the saved CSV file or None if data is empty.
        """
        try:
            data = self.fetch_historical_data(start_date, end_date)
            if not data.empty:
                file_path = os.path.join(output_path, f"{self.ticker}_data.csv")
                data.to_csv(file_path)
                print(f'Data saved to {file_path}')
                return file_path
            else:
                print(f'No data to save.')
                return None
        except Exception as e:
            print(f'Error saving data: {e}')
            return None
        
    def plot_data(self, data, predictions, end_date, prediction_days):
        """
        Plots historical stock data and predicted future stock prices.
        
        Args:
            hist_data (pd.DataFrame): Historical stock data.
            predictions (list): A list of predicted future stock prices.
            end_date (datetime): The end date of the historical data.
            prediction_days (int): The number of prediction days to display.
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            
            future_dates = [end_date + timedelta(days=i) for i in range(1, prediction_days + 1)]
            
            print(f'Historical data shape: {data.shape}')
            print(f'Predictions shape: {len(predictions)}')
            print(f'Future dates shape: {len(future_dates)}')
            
            plt.figure(figsize=(10, 6))
            plt.plot(data.index, data['Close'], label='Historical Prices')
            plt.plot(future_dates, predictions, label='Predicted Prices', color='red', linestyle='--')
    
            todays_date = datetime.today()
            plt.axvline(todays_date, color='green', linestyle='--', label='Today')
            
            # Labels and title
            
            plt.xlabel("Date")
            plt.ylabel("Price")
            plt.title(f"{self.ticker} Stock Price Prediction")
            plt.legend()
            plt.grid()
            plt.tight_layout()
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            plt.xticks(rotation=45)
            plt.show()
            print('Stock price plot generated.')
        except Exception as e:
            print(f'Error plotting: {e}')
            
    def generate_prediction_plot(self, days=None, time_steps=None, prediction_days=60):
        """
        Generates a prediction plot for future stock prices using the random tree regression.
        
        Args:
            days (int, optional): The number of days to look back for historical data. Defaults to None.
            time_steps (int, optional): The number of time steps for machine learning model. Defaults to None.
            prediction_days (int): The number of future days to predict. Defaults to 60.
        """
        # If days are not provided, use the default value of 5 years
        if days is None:
            end_date = datetime.today()
        else:
            end_date = datetime.today() - timedelta(days=days)
        
        # if time_steps are not provided, use the default value of 30
        if time_steps is None:
            time_steps = 30
        
        # Fetch historical data depending on the end date
        start_date = end_date - timedelta(days=5*365)
        hist_data = self.fetch_historical_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        if hist_data.empty:
            print(f'No historical data found. Exiting')
        
        x, y = self.training.transform_data(hist_data, time_steps) # Transform the data for machine learning
        
        #####################
        
        
        if x is not None and y is not None:
            model = self.training.train_and_evaluate(x, y)[0]
        if model:
            predictions = self.training.predict_future_prices(model, x[-time_steps:], prediction_days)
            self.plot_data(hist_data, predictions, end_date, prediction_days)