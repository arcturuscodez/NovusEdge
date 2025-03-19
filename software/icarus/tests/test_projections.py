import sys
from pathlib import Path

# Add parent directory to path BEFORE other imports
sys.path.append(str(Path(__file__).parent.parent))
from analysis.finance import FinnishCorporateTaxCalculator
from analysis.oracle import Oracle
from analysis.forecasting import project_portfolio_growth
from decimal import Decimal
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))

def test_portfolio() -> None:
    """Test portfolio growth projection."""
    tickers = ['HDLV.PA', 'VGWD.DE']

    custom_yields = {
        'HDLV.PA': Decimal('0.0336'),  # Custom yield for HDLV.PA
        'VGWD.DE': Decimal('0.0295')  # Custom yield for VGWD.DE
    }

    retrievers = {ticker: Oracle(ticker) for ticker in tickers}
    
    portfolio_data = {}
    total_value = Decimal('0')
    shares = 50

    for ticker, retriever in retrievers.items():
        price = Decimal(str(retriever.get_latest_closing_price() or 0))
        div_yield = retriever.get_dividend_yield()
        if div_yield is None or div_yield == Decimal('0'):
            div_yield = custom_yields.get(ticker, Decimal('0'))  # Use custom yield if retrieval fails
        
        portfolio_data[ticker] = {
            'price': price,
            'div_yield': div_yield
        }
        
        total_value += price * Decimal(shares)

    avg_div_yield = sum(d['div_yield'] for d in portfolio_data.values()) / Decimal(str(len(portfolio_data)))
    
    results = project_portfolio_growth(
        tax_calculator=FinnishCorporateTaxCalculator(),
        initial_value=total_value,
        dividend_yield=avg_div_yield,
        foreign_withholding_rate=Decimal('0.15'),
        years=10,
        dividend_growth_rate=Decimal('0.02'),
        asset_growth_rate=Decimal('0.03')
    )
    
    rounded_results = [
        {
            'year': r['year'],
            'portfolio_value': float(Decimal(r['portfolio_value']).quantize(Decimal('0.01'))),
            'dividend_income': float(Decimal(r['dividend_income']).quantize(Decimal('0.01'))),
            'finnish_tax': float(Decimal(r['finnish_tax']).quantize(Decimal('0.01'))),
            'total_tax': float(Decimal(r['total_tax']).quantize(Decimal('0.01'))),
            'after_tax_cash': float(Decimal(r['after_tax_cash']).quantize(Decimal('0.01')))
        }
        for r in results
    ]
    
    print("\nPortfolio Details:")
    for ticker, data in portfolio_data.items():
        print(f"{ticker}:")
        print(f"  Price: €{data['price']:.2f}")
        print(f"  Dividend Yield: {float(data['div_yield'] * 100):.2f}%")
    
    print(f"\nTotal Portfolio Value: €{total_value:.2f}")
    print(f"Average Dividend Yield: {float(avg_div_yield * 100):.2f}%")
    
    print("\nProjection Results:")
    df = pd.DataFrame(rounded_results)
    print(df.to_string(index=False, justify='right'))

if __name__ == "__main__":
    test_portfolio()