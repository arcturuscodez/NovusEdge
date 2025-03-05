from finance import FinnishCorporateTaxCalculator
from retriever import AssetRetriever
from analysis import project_portfolio_growth
from decimal import Decimal
import pandas as pd

def test_portfolio() -> None:
    """Test portfolio growth projection."""
    tickers = ['O', 'KO', 'BA.L']
    retrievers = {ticker: AssetRetriever(ticker) for ticker in tickers}
    
    portfolio_data = {}
    total_value = Decimal('0')
    
    for ticker, retriever in retrievers.items():
        price = Decimal(str(retriever.get_latest_closing_price() or 0))
        div_yield = retriever.get_dividend_yield() or Decimal('0')
        
        portfolio_data[ticker] = {
            'price': price,
            'div_yield': div_yield
        }
        
        total_value += price * 100

    avg_div_yield = sum(d['div_yield'] for d in portfolio_data.values()) / Decimal(str(len(portfolio_data)))
    
    results = project_portfolio_growth(
        tax_calculator=FinnishCorporateTaxCalculator(),
        initial_value=total_value,
        dividend_yield=avg_div_yield,
        foreign_withholding_rate=Decimal('0.15'),
        years=10,
        dividend_growth_rate=Decimal('0.02')
    )
    
    rounded_results = [
        {
            'year': r['year'],
            'portfolio_value': float(r['portfolio_value'].quantize(Decimal('0.01'))),
            'dividend_income': float(r['dividend_income'].quantize(Decimal('0.01'))),
            'finnish_tax': float(r['finnish_tax'].quantize(Decimal('0.01'))),
            'total_tax': float(r['total_tax'].quantize(Decimal('0.01'))),
            'after_tax_cash': float(r['after_tax_cash'].quantize(Decimal('0.01')))
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