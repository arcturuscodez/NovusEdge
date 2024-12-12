from database import Database
from security import credentials
from stocks import StocksManager as sm

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class Simulator:
    
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
    
    def monte_carlo_simulation(self, hist_data, days, simulations):
        """
        Monte Carlo simulation for stock price predictions.

        This simulation models potential future prices of a stock by repeatedly 
        sampling from its historical daily returns. It uses the geometric Brownian 
        motion (GBM) model, a standard mathematical approach for simulating 
        stochastic processes in financial modeling.

        Args:
            hist_data (pd.DataFrame): Historical data for the stock.
            days (int): Number of days to simulate.
            simulations (int): Number of simulation runs.

        Returns:
            list: Simulated end prices after the given period.
        """
        try:
            last_price = hist_data['Close'].iloc[-1]
            daily_returns = hist_data['Close'].pct_change().dropna()
            mean_return = daily_returns.mean()
            std_dev = daily_returns.std()
            print(f"Simulating with last price: {last_price}, Mean return: {mean_return}, Std dev: {std_dev}")

            simulated_prices = []
            for _ in range(simulations):
                prices = [last_price]
                for _ in range(days):
                    drift = mean_return - (0.5 * std_dev**2)
                    shock = std_dev * np.random.normal()
                    price = max(prices[-1] * np.exp(drift + shock), 0.01)  # Prevent negative or zero prices
                    prices.append(price)
                simulated_prices.append(prices[-1])

            return simulated_prices
        except Exception as e:
            print(f"Error in Monte Carlo simulation: {e}")
            return []

    def simulate(self, ticker, days=365, simulations=100, simulation_type='monte_carlo'):
        """ 
        Simulate future performance of a stock using specified simulation type.

        Args:
            ticker (str): Stock ticker.
            days (int): Number of days to simulate.
            simulations (int): Number of iterations.
            simulation_type (str): Type of simulation to run (e.g., 'monte_carlo').

        Returns:
            list: A list of simulated end prices.
        """
        try:
            hist_data = sm.fetch_testing_data(ticker)
            if hist_data.empty:
                print(f"No historical data for {ticker}. Cannot run simulations.")
                return []

            if simulation_type == 'monte_carlo':
                return self.monte_carlo_simulation(hist_data, days, simulations)
            else:
                print(f"Unknown simulation type: {simulation_type}")
                return []
            
        except Exception as e:
            print(f'Error running core simulate method: {e}')

if __name__ == "__main__":
    sim = Simulator()

    # Run a Monte Carlo simulation for 'GME'
    for record in sim.portfolio:
        firm_id, ticker, shares, avg_price, total_invested, *_ = record
        print(f"Simulating for {ticker}...")

        # Run Monte Carlo simulations
        simulated_prices = sim.simulate(ticker, days=252, simulations=100, simulation_type='monte_carlo')

        # Print results
        if simulated_prices:
            print(f"{ticker}: Simulated average price after 252 days: {sum(simulated_prices) / len(simulated_prices):.2f}")
            print(f"{ticker}: Simulated price range: {min(simulated_prices):.2f} - {max(simulated_prices):.2f}")

