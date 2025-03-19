import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from analysis.portfolio.generator import PortfolioGenerator

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    generator = PortfolioGenerator()
    
    # Load tickers
    tickers = generator.load_tickers("tickers.csv")
    print(f"Loaded {len(tickers)} tickers")
    
    # Fetch data for criteria
    attributes = ['dividend_yield', 'price']
    generator.fetch_ticker_data(tickers, attributes, sample_size=100)
    
    # Clear existing criteria
    generator.criteria = {}
    
    # Add range-based dividend yield criterion (between 2.5% and 3.5%)
    generator.add_dividend_yield_range(min_yield=0.025, max_yield=0.035)
    
    # Add price criterion (under $100)
    generator.add_range_criterion(
        name="affordable_price",
        attribute="price",
        max_value=100.0,
        weight=0.3,
        description="Stock price under $100"
    )
    
    # Generate portfolios with the new criteria
    portfolios = generator.generate_portfolios(
        num_portfolios=5,
        stocks_per_portfolio=8
    )
    
    print("\n=== GENERATED PORTFOLIOS ===")
    for i, portfolio in enumerate(portfolios):
        print(f"Portfolio {i+1}: {', '.join(portfolio)}")
        
        # Print dividend yields for this portfolio
        print("  Dividend Yields:")
        for ticker in portfolio:
            if ticker in generator.ticker_data and 'dividend_yield' in generator.ticker_data[ticker]:
                yield_value = float(generator.ticker_data[ticker]['dividend_yield']) * 100
                print(f"  {ticker}: {yield_value:.2f}%")
        print()

if __name__ == "__main__":
    main()