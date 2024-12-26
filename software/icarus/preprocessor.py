from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
import yfinance as yf

class Preproccessor:
    
    def __init__(self):
        self.scaler = MinMaxScaler()
        
    def fetch_historical_data(self, start_date, end_date, ticker):
        """
        Fetches historical stock data between specified start and end dates.
        
        Args:
            start_date (str): The start date for the historical data (YYYY-MM-DD).
            end_date (str): The end date for the historical data (YYYY-MM-DD).
            ticker (str): The stock ticker.
        
        Returns:
            pd.DataFrame: A DataFrame containing the historical stock data.
        """
        try:
            data = yf.download(ticker, start=start_date, end=end_date)
            print(f'Fetched historical data for {ticker}')
            return data
        except Exception as e:
            print(f'Error fetching historical data: {e}')
            return pd.DataFrame()
    
    def transform_data(self, data, time_steps=60):
        """ 
        Transform stock data for machine learning by scaling and creating sequences of historical data.
        
        Args:
            data (pd.DataFrame): The stock data to be transformed.
            time_steps (int, optional): The number of time steps to look back when creating sequences. Defaults to 60.
            
        Returns:
            tuple: Two numpy arrays, x (input data) and y (target data) for machine learning.
        """
        try:
            scaled_data = self.scaler.fit_transform(data[['Close']])
            
            print(f'Scaled data : {scaled_data}')
            
            x, y = [], []
            
            print(f'x : {x}, y : {y} AFTER CREATION OF SCALED DATA')
            
            for i in range(time_steps, len(scaled_data)):
                x.append(scaled_data[i - time_steps:i, 0])
                y.append(scaled_data[i, 0])
            
            x, y = np.array(x), np.array(y)
            
            print(f'Shape of x: {x.shape}')
            print(f'Shape of y: {y.shape}')
            
            x = x.reshape(x.shape[0], x.shape[1])
            
            print(x)
            print(x.shape)
            
            return x, y
            
        except Exception as e:
            print(f'Error transforming data: {e}')
            return None, None
        
if __name__=='__main__':
    
    dp = Preproccessor()
    ticker = 'AAPL'

    data = dp.fetch_historical_data('2000-01-01', '2024-12-14', ticker)
    
    dp.transform_data(data, 60)