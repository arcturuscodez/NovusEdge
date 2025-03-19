import pandas as pd
import random
from decimal import Decimal
from typing import List, Dict, Tuple
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from icarus.analysis.oracle import Oracle
from icarus.analysis.forecasting import project_portfolio_growth
from icarus.analysis.finance import FinnishCorporateTaxCalculator

def load_tickers(csv_path: str) -> List[str]:
    """Load tickers from CSV file."""
    df = pd.read_csv(csv_path)
    return df['Ticker'].tolist()

def check_dividend_yields(tickers: List[str], sample_size: int = None) -> Dict[str, Decimal]:
    """Check dividend yields for tickers, optionally using a sample."""
    if sample_size:
        tickers = random.sample(tickers, min(sample_size, len(tickers)))
    
    results = {}
    total = len(tickers)
    
    print(f"Checking dividend yields for {total} tickers...")
    
    for i, ticker in enumerate(tickers, 1):
        if i % 10 == 0:
            print(f"Progress: {i}/{total} ({(i/total)*100:.1f}%)")
            
        try:
            oracle = Oracle(ticker)
            div_yield = oracle.get_dividend_yield()
            
            if div_yield is not None and div_yield > Decimal('0'):
                results[ticker] = div_yield
                print(f"Found yield for {ticker}: {float(div_yield)*100:.2f}%")
        except Exception as e:
            print(f"Error processing {ticker}: {str(e)}")
            
    return results

def generate_portfolios(yield_data: Dict[str, Decimal], 
                        num_portfolios: int = 10, 
                        stocks_per_portfolio: int = 8) -> List[Dict[str, Decimal]]:
    """Generate portfolios based on dividend yield data."""
    # Filter tickers with valid yields
    valid_tickers = list(yield_data.keys())
    
    if len(valid_tickers) < stocks_per_portfolio:
        raise ValueError(f"Not enough valid tickers ({len(valid_tickers)}) to create portfolios of {stocks_per_portfolio} stocks")
    
    portfolios = []
    
    # Create portfolios
    for i in range(num_portfolios):
        # Mix of high, medium and low yield stocks for diversification
        sorted_tickers = sorted(valid_tickers, key=lambda t: yield_data[t], reverse=True)
        
        high_yield = sorted_tickers[:len(sorted_tickers)//3]
        mid_yield = sorted_tickers[len(sorted_tickers)//3:2*len(sorted_tickers)//3]
        low_yield = sorted_tickers[2*len(sorted_tickers)//3:]
        
        # Create a mix based on portfolio number
        if i % 3 == 0:  # Yield-focused portfolio
            selected = random.sample(high_yield, min(5, len(high_yield)))
            selected += random.sample(mid_yield + low_yield, stocks_per_portfolio - len(selected))
        elif i % 3 == 1:  # Balanced portfolio
            selected = random.sample(mid_yield, min(5, len(mid_yield)))
            selected += random.sample(high_yield + low_yield, stocks_per_portfolio - len(selected))
        else:  # Growth-focused portfolio
            selected = random.sample(low_yield, min(5, len(low_yield)))
            selected += random.sample(high_yield + mid_yield, stocks_per_portfolio - len(selected))
            
        random.shuffle(selected)
        selected = selected[:stocks_per_portfolio]
        
        portfolio = {ticker: yield_data[ticker] for ticker in selected}
        portfolios.append(portfolio)
        
    return portfolios

def evaluate_portfolios(portfolios: List[Dict[str, Decimal]], 
                        years: int = 10, 
                        initial_value: Decimal = Decimal('1000000')) -> List[Tuple[int, Dict, Dict]]:
    """Evaluate all portfolios and return them ranked by total return."""
    tax_calculator = FinnishCorporateTaxCalculator()
    results = []
    
    for i, portfolio in enumerate(portfolios):
        # Calculate portfolio average dividend yield
        avg_div_yield = sum(portfolio.values()) / Decimal(str(len(portfolio)))
        
        # Project growth
        projection = project_portfolio_growth(
            tax_calculator=tax_calculator,
            initial_value=initial_value,
            dividend_yield=avg_div_yield,
            foreign_withholding_rate=Decimal('0.15'),
            years=years,
            dividend_growth_rate=Decimal('0.02'),
            asset_growth_rate=Decimal('0.07')
        )
        
        # Calculate final stats
        final_value = projection[-1]['portfolio_value']
        total_return = (final_value / initial_value - 1) * 100
        
        results.append((i, portfolio, {
            'avg_yield': float(avg_div_yield * 100),
            'final_value': float(final_value),
            'total_return': float(total_return),
            'projection': projection
        }))
    
    # Sort by total return
    results.sort(key=lambda x: x[2]['total_return'], reverse=True)
    return results

def main():
    # Path to tickers CSV
    tickers_csv = Path(__file__).parent.parent / "data" / "processed" / "tickers.csv"
    
    # Load tickers
    tickers = load_tickers(str(tickers_csv))
    print(f"Loaded {len(tickers)} tickers")
    
    # Check dividend yields (using a sample for testing)
    sample_size = 100  # Adjust as needed
    yield_data = check_dividend_yields(tickers, sample_size)
    print(f"Found {len(yield_data)} tickers with dividend yields")
    
    # Generate portfolios
    num_portfolios = 10
    stocks_per_portfolio = 8
    portfolios = generate_portfolios(yield_data, num_portfolios, stocks_per_portfolio)
    
    # Evaluate portfolios
    results = evaluate_portfolios(portfolios)
    
    # Display results
    print("\n=== PORTFOLIO EVALUATION RESULTS ===")
    print(f"Evaluated {len(results)} portfolios over 10 years\n")
    
    for rank, (portfolio_id, stocks, stats) in enumerate(results, 1):
        print(f"Rank #{rank} - Portfolio {portfolio_id + 1}")
        print(f"Tickers: {', '.join(stocks.keys())}")
        print(f"Average Dividend Yield: {stats['avg_yield']:.2f}%")
        print(f"Final Value: €{stats['final_value']:,.2f}")
        print(f"Total Return: {stats['total_return']:.2f}%")
        print("-" * 50)

if __name__ == "__main__":
    main()