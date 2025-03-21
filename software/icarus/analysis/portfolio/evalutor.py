import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import logging
from decimal import Decimal
from typing import List, Dict
import pandas as pd
from generator import PortfolioGenerator, TickerConfig
from analysis.forecasting import project_portfolio_growth
from analysis.finance import FinnishCorporateTaxCalculator

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def evaluate_portfolios(num_portfolios: int, config: TickerConfig, tax_calculator: FinnishCorporateTaxCalculator,
                       initial_value: Decimal, years: int, foreign_withholding_rate: Decimal = Decimal('0.15'),
                       dividend_growth_rate: Decimal = Decimal('0.02'), asset_growth_rate: Decimal = None,
                       use_historical_growth: bool = True, historical_years: int = 10) -> List[Dict]:
    """
    Generate portfolios and evaluate their projected growth over time.

    Args:
        num_portfolios: Number of portfolios to generate.
        config: TickerConfig object with portfolio generation parameters.
        tax_calculator: FinnishCorporateTaxCalculator instance for tax calculations.
        initial_value: Starting portfolio value in euros.
        years: Number of years to project.
        foreign_withholding_rate: Foreign withholding tax rate on dividends.
        dividend_growth_rate: Annual dividend growth rate.
        asset_growth_rate: Fallback annual asset growth rate if historical data unavailable.
        use_historical_growth: Whether to use historical growth rates from Oracle.
        historical_years: Number of years to use for historical growth calculation.

    Returns:
        List of dictionaries with portfolio evaluation results.
    """

    if asset_growth_rate is None:
        asset_growth_rate = Decimal('0.07')
        
    from analysis.oracle import Oracle
    
    generator = PortfolioGenerator()
    try:
        portfolios = generator.generate_portfolios(num_portfolios, config, strategy='performance_optimized')
    except Exception as e:
        logger.error(f"Failed to generate portfolios: {str(e)}")
        return []

    enriched_data = generator.loader.load_enriched_data()
    if enriched_data.empty:
        logger.error("No enriched data available for evaluation")
        return []

    results = []
    for i, portfolio in enumerate(portfolios):
        logger.info(f"Evaluating portfolio {i+1}: {portfolio}")
        
        try:
            avg_dividend_yield = float(enriched_data.loc[portfolio, 'Dividend_Yield'].mean())
            if pd.isna(avg_dividend_yield):
                logger.warning(f"Portfolio {i} has missing dividend yield data, using default 0.03")
                avg_dividend_yield = 0.03
        except KeyError:
            logger.warning(f"Portfolio {i} contains tickers not in enriched data, using default 0.03")
            avg_dividend_yield = 0.03
        
        portfolio_growth_rate = asset_growth_rate
        if use_historical_growth:
            growth_rates = []
            valid_rates = 0
            
            for ticker in portfolio:
                try:
                    oracle = Oracle(ticker)
                    ticker_growth = oracle.get_growth_rate(years=historical_years)
                    
                    if ticker_growth is not None:
                        growth_rates.append(ticker_growth)
                        valid_rates += 1
                        logger.info(f"Historical growth rate for {ticker}: {ticker_growth:.4f}")
                except Exception as e:
                    logger.warning(f"Failed to get growth rate for {ticker}: {e}")
            
            if valid_rates > 0:
                avg_growth_rate = sum(growth_rates) / Decimal(str(valid_rates))
                portfolio_growth_rate = avg_growth_rate
                logger.info(f"Using average historical growth rate: {portfolio_growth_rate:.4f}")
            else:
                logger.warning(f"No valid historical growth rates for portfolio {i}, using fallback rate: {asset_growth_rate}")
        
        try:
            projection = project_portfolio_growth(
                tax_calculator=tax_calculator,
                initial_value=initial_value,
                dividend_yield=Decimal(str(avg_dividend_yield)),
                foreign_withholding_rate=foreign_withholding_rate,
                years=years,
                dividend_growth_rate=dividend_growth_rate,
                asset_growth_rate=portfolio_growth_rate
            )
            final_value = projection[-1]['portfolio_value']
            total_return = (final_value - initial_value) / initial_value
            annualized_return = (1 + total_return) ** (Decimal('1') / Decimal(str(years))) - 1 if years > 0 else Decimal('0')
        except Exception as e:
            logger.error(f"Projection failed for portfolio {i}: {str(e)}")
            continue

        results.append({
            "portfolio": portfolio,
            "projection": projection,
            "final_value": final_value,
            "annualized_return": annualized_return,
            "growth_rate_used": portfolio_growth_rate
        })

    results.sort(key=lambda x: x['annualized_return'], reverse=True)
    return results

def main():
    # Setup
    tax_calculator = FinnishCorporateTaxCalculator()
    config = TickerConfig(
        min_dividend_yield=0.02,
        max_dividend_yield=0.06,
        max_pe_ratio=25,
        min_market_cap=5_000_000_000,
        sectors={"Technology", "Healthcare", "Consumer Defensive", "Financials"},
        max_beta=1.5,
        num_stocks=8,
        max_stocks_per_sector=2,
        min_eps_growth=0.05,
        min_roe=0.10
    )

    results = evaluate_portfolios(
        num_portfolios=5,
        config=config,
        tax_calculator=tax_calculator,
        initial_value=Decimal('100000'),
        years=5,
        foreign_withholding_rate=Decimal('0.15'),
        dividend_growth_rate=Decimal('0.02'),
        use_historical_growth=True,
        historical_years=15,
        asset_growth_rate=Decimal('0.07')  # Fallback rate if historical data unavailable
    )

    print(f"Evaluated {len(results)} portfolios:")
    for i, result in enumerate(results):
        portfolio = result['portfolio']
        final_value = result['final_value']
        annualized_return = result['annualized_return']
        projections = result['projection']

        return_percentage = f"{float(annualized_return) * 100:.2f}%"

        print(f"\nPortfolio {i} ({len(portfolio)} stocks): {portfolio}")
        print(f"Final Value: {final_value:.2f} EUR")
        print(f"Annualized Return: {return_percentage}")
        print("Yearly Projections:")

        for year, proj in enumerate(projections):
            print(f"  Year {year}: Value={proj['portfolio_value']:.2f}, Div={proj['dividend_income']:.2f}, Tax={proj['total_tax']:.2f}")
if __name__ == "__main__":
    main()