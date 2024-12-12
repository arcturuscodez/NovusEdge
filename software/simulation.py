from database import Database
from security import credentials

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class Simulations:
    
    def __init__(self):
        """Set up the class for simulating portfolio performance."""
        self.portfolio = []
        
        with Database(db=credentials.DB, 
                      user=credentials.USER, 
                      password=credentials.PASSWORD, 
                      host=credentials.HOST, 
                      port=credentials.PORT, 
                      pg_exe=credentials.PG_EXE_PATH,
                    ) as self.db:
                        self.portfolio = self.db.fetch_data('PORTFOLIO')
                        print("Portfolio fetched:", self.portfolio)
        
    def fetch_historical_data(self, ticker, period='1y'):
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
        
    def simulate(self, ticker, days=252, simulations=100):
        """ 
        Simulate future performance of a stock using historical data.
        
        Args:
            ticker (str): Stock ticker.
            days (int): Numbeer of days to simulate.
            simulations (int): Number of iterations
            
        Returns:
            list: A list of simulated end prices.    
        """
        hist = self.fetch_historical_data(ticker)
        if hist.empty:
            print(f'No data avaiable for ticker {ticker}. Simulation aborted.')
            return []
        
        hist['Daily Return'] = hist['Close'].pct_change()
        mean_return = hist['Daily Return'].mean()
        std_dev_return = hist['Daily Return'].std()
        
        simulated_prices = []
        last_price = hist['Close'].iloc[-1]
        
        for _ in range(simulations):
            prices = [last_price]
            for _ in range(days):
                drift = mean_return - (0.5 * std_dev_return ** 2)
                shock = np.random.normal(0, std_dev_return)
                price = prices[-1] * np.exp(drift + shock)
                prices.append(price)
            simulated_prices.append(prices[-1])
            
        print(f'Simulation complete for {ticker}')
        return simulated_prices

if __name__ == "__main__":
    sim = Simulations()
    for record in sim.portfolio:
        firm_id, ticker, shares, avg_price, total_invested, *_ = record
        print(f'Simulating for {ticker}')
        simulated_prices = sim.simulate(ticker, days=252, simulations=100)
        
        if simulated_prices:
            print(f"{ticker}: Simulated average price after 252 days: {sum(simulated_prices) / len(simulated_prices):.2f}")
            print(f"{ticker}: Simulated price range: {min(simulated_prices):.2f} - {max(simulated_prices):.2f}")

