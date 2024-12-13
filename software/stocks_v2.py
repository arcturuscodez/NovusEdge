import os
import random
import plotting
import numpy as np
import pandas as pd
import yfinance as yf

from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

class StockDataFetcher:
    """ 
    Service to fetch stock data from external sources (e.g., Yahoo Finance.)
    This class provides methods to fetch stock data and dividend information for a given ticker.
    """
    @staticmethod
    def fetch_stock_data(ticker):
        """
        Acquire the latest stock data for the given ticker.
        
        Args:
            ticker (str): The stock ticker symbol (e.g., 'AAPL', 'GOOG').
        
        Returns:
            tuple: The current stock price and the most recent quarterly dividend amount (if available).
            If no dividend data is available, returns (None, None).
        """
        stock = yf.Ticker(ticker)
        dividend_data = stock.dividends
        current_price = float(stock.history(period='1d')['Close'].iloc[0])
        
        if not dividend_data.empty:
            quarterly_latest_dividend_amount = float(dividend_data.iloc[-1])
            return current_price, quarterly_latest_dividend_amount
        else:
            print(f'No dividend data available for {ticker}')
            return None, None
        
class StockDataManager:
    """Class for the management and analysis of stock data."""
    
    def __init__(self, ticker):
        """
        Initializes the StockDataManager instance with a stock ticker symbol.
        
        Args:
            ticker (str): The stock ticker symbol (e.g., 'AAPL', 'GOOG').
        """
        self.ticker = ticker
        self.stock = yf.Ticker(self.ticker)
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        
    def get_basic_info(self):
        """
        Fetches basic stock information such as company name, sector, and website.
        
        Returns:
            dict: A dictionary containing key information about the stock.
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
            print(f'Error fetching stock info: {e}')
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
        
    def transform_data(self, data, time_steps):
        """
        Prepares stock data for machine learning by scaling and creating sequences of historical data.
        
        Args:
            data (pd.DataFrame): The stock data to be transformed.
            time_steps (int): The number of time steps to look back when creating sequences.
        
        Returns:
            tuple: Two numpy arrays, x (input data) and y (target data) for machine learning.
        """
        try:
            scaled_data = self.scaler.fit_transform(data[['Close']])
            x, y = [], []
            
            for i in range(time_steps, len(scaled_data)):
                x.append(scaled_data[i - time_steps:i, 0])
                y.append(scaled_data[i, 0])
            
            x, y = np.array(x), np.array(y)
            x = x.reshape(x.shape[0], x.shape[1])
            
            print('Data transformed for machine learning.')
            return x, y
        except Exception as e:
            print(f'Error transforming data: {e}')
            return None, None
        
    def generate_synthetic_data(self, start_price, time_steps, days):
        """
        Generates synthetic stock data for testing or simulation purposes.
        
        Args:
            start_price (float): The starting price for the synthetic data.
            time_steps (int): The number of time steps for the synthetic data.
            days (int): The number of days to generate synthetic data for.
        
        Returns:
            pd.DataFrame: A DataFrame containing the generated synthetic stock data.
        """
        try:
            dates = [datetime.today() + timedelta(days=i) for i in range(days)]
            prices = [start_price]

            for _ in range(1, days):
                change = random.uniform(-0.03, 0.03)
                new_price = max(0, prices[-1] * (1 + change))
                prices.append(new_price)

            data = pd.DataFrame({"Date": dates, "Close": prices}).set_index("Date")
            print("Synthetic data generated.")
            return data
        except Exception as e:
            print(f'Error generating synthetic data: {e}')
            return []
    
    def validate_data(self, data):
        """
        Performs basic validation on stock data by checking if the data is empty
        and computing basic statistics such as mean, standard deviation, min, and max.
        
        Args:
            data (pd.DataFrame): The stock data to validate.
        
        Returns:
            bool: True if data is valid, False if data is empty or invalid.
        """
        try:
            if data.empty:
                print('Data validation failed: DataFrame is empty.')
                return False
            
            stats = {
                "mean": data["Close"].mean(),
                "std": data["Close"].std(),
                "min": data["Close"].min(),
                "max": data["Close"].max()
            }
            
            print(f'Data validation stats: {stats}')
            return True
        except Exception as e:
            print(f'Error validating data: {e}')
            return False
        
    def calclate_technical_indicators(self, data):
        """
        Calculates key technical indicators such as Simple Moving Average (SMA),
        Exponential Moving Average (EMA), and Relative Strength Index (RSI).
        
        Args:
            data (pd.DataFrame): The stock data to calculate indicators for.
        
        Returns:
            pd.DataFrame: The original data with new columns for SMA, EMA, and RSI.
        """
        try:
            data.loc[:, 'SMA_20'] = data['Close'].rolling(window=20).mean()
            data.loc[:, 'EMA_20'] = data['Close'].ewm(span=20, adjust=False).mean()
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta <0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data.loc[:, 'RSI'] = 100 - (100 / (1 + rs))
            print('Technical indicators calculated.')
            return data
        except Exception as e:
            print(f'Error calculating technical indicators: {e}')
            return data
    
    def train_model_random_forest_regression(self, x, y):
        """
        Random Forest Regression for stock price predictions.
        
        This method uses a trained Random Forest model to predict future stock 
        prices based on historical data sequences. The model is trained on past 
        stock prices and makes predictions based on the most recent sequence 
        of data.

        Args:
            x (np.array): The sequence of historical stock data to predict from.
            y (np.array): The target values (future stock prices) for training.
        
        Returns:
            model (RandomForestRegressor): A trained Random Forest model.
        """
        try:
            x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(x_train, y_train)
            score = model.score(x_test, y_test)
            print(f'Model trained with score: {score}')
            return model
        
        except Exception as e:
            print(f'Error training model: {e}')
            return None
    
    def predict_future_prices(self, time_steps, model, recent_data, prediction_days):
        """
        Predict future stock prices using a trained Random Forest model.
        
        Args:
            time_steps (int): The number of time steps for prediction.
            model (RandomForestRegressor): The trained model to make predictions.
            recent_data (np.array): The most recent stock data to base predictions on.
            prediction_days (int): The number of days to predict into the future.
        
        Returns:
            list: A list of predicted stock prices for the specified number of days.
        """
        try:
            predictions = []
            last_sequence = recent_data[-1].reshape(1, -1)
            
            for _ in range(prediction_days):
                next_pred = model.predict(last_sequence)
                predictions.append(next_pred[0])
                last_sequence = np.append(last_sequence[:, 1:], [[next_pred[0]]], axis=1)
                
            predictions = self.scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()
            print('Stock price predictions generated.')
            return predictions
        
        except Exception as e:
            print(f'Error predicting stock prices: {e}')
            return []
            
    def plot_stock_predictions(self, hist_data, predictions, end_date, prediction_days):
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
            
            plt.figure(figsize=(10, 6))
            plt.plot(hist_data.index, hist_data['Close'], label='Historical Prices')
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
    
    def generate_prediction_plot(self, days = None, time_steps = None, prediction_days=60):
        """
        Generates a prediction plot for future stock prices.
        
        Args:
            days (int, optional): The number of days to look back for historical data. Defaults to None.
            time_steps (int, optional): The number of time steps for machine learning model. Defaults to None.
            prediction_days (int): The number of future days to predict. Defaults to 60.
        """
        if days is None:
            end_date = datetime.today()
        else:
            end_date = datetime.today() - timedelta(days=days)
        
        if time_steps is None:
            time_steps = 30
        
        start_date = end_date - timedelta(days=5*365)
        hist_data = self.fetch_historical_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        if hist_data.empty:
            print(f'No historical data found. Exiting')
        
        x, y = self.transform_data(hist_data, time_steps)
        if x is not None and y is not None:
            model = self.train_model_random_forst_regression(x, y)
        if model:
            predictions = self.predict_future_prices(time_steps, model, x, prediction_days)
            self.plot_stock_predictions(hist_data, predictions, end_date, prediction_days)
    
            