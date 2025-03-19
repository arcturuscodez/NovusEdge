import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import logging
from decimal import Decimal
from typing import List, Dict
import pandas as pd
from generator import PortfolioGenerator, TickerConfig  # Import from generator.py
from analysis.forecasting import project_portfolio_growth
from analysis.finance import FinnishCorporateTaxCalculator

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def evaluate_portfolios(num_portfolios: int, config: TickerConfig, tax_calculator: FinnishCorporateTaxCalculator,
                       initial_value: Decimal, years: int, foreign_withholding_rate: Decimal = Decimal('0.15'),
                       dividend_growth_rate: Decimal = Decimal('0.02'), asset_growth_rate: Decimal = Decimal('0.07')) -> List[Dict]:
    """
    Generate portfolios and evaluate their projected growth over time using the original forecasting function.

    Args:
        num_portfolios: Number of portfolios to generate.
        config: TickerConfig object with portfolio generation parameters.
        tax_calculator: FinnishCorporateTaxCalculator instance for tax calculations.
        initial_value: Starting portfolio value in euros.
        years: Number of years to project.
        foreign_withholding_rate: Foreign withholding tax rate on dividends.
        dividend_growth_rate: Annual dividend growth rate.
        asset_growth_rate: Annual asset growth rate.

    Returns:
        List of dictionaries, each containing:
        - portfolio: List of ticker symbols.
        - projection: List of yearly growth projections from project_portfolio_growth.
        - final_value: Final portfolio value after 'years'.
        - annualized_return: Annualized return over the projection period.
    """
    # Generate portfolios
    generator = PortfolioGenerator()
    try:
        portfolios = generator.generate_portfolios(num_portfolios, config, strategy='performance_optimized')
    except Exception as e:
        logger.error(f"Failed to generate portfolios: {str(e)}")
        return []

    # Get enriched data for metric calculations
    enriched_data = generator.loader.load_enriched_data()
    if enriched_data.empty:
        logger.error("No enriched data available for evaluation")
        return []

    results = []
    for i, portfolio in enumerate(portfolios):
        # Calculate average dividend yield for the portfolio
        try:
            avg_dividend_yield = float(enriched_data.loc[portfolio, 'Dividend_Yield'].mean())  # Ensure float
            if pd.isna(avg_dividend_yield):
                logger.warning(f"Portfolio {i} has missing dividend yield data, using default 0.03")
                avg_dividend_yield = 0.03
        except KeyError:
            logger.warning(f"Portfolio {i} contains tickers not in enriched data, using default 0.03")
            avg_dividend_yield = 0.03

        # Project growth using the original function signature
        try:
            projection = project_portfolio_growth(
                tax_calculator=tax_calculator,
                initial_value=initial_value,
                dividend_yield=Decimal(str(avg_dividend_yield)),
                foreign_withholding_rate=foreign_withholding_rate,
                years=years,
                dividend_growth_rate=dividend_growth_rate,
                asset_growth_rate=asset_growth_rate
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
            "annualized_return": annualized_return
        })

    # Sort by annualized return for ranking
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

    # Evaluate portfolios
    results = evaluate_portfolios(
        num_portfolios=5,
        config=config,
        tax_calculator=tax_calculator,
        initial_value=Decimal('100000'),
        years=5,
        foreign_withholding_rate=Decimal('0.15'),
        dividend_growth_rate=Decimal('0.02'),
        asset_growth_rate=Decimal('0.07')
    )

    # Print results
    print(f"Evaluated {len(results)} portfolios:")
    for i, result in enumerate(results):
        print(f"\nPortfolio {i + 1} ({len(result['portfolio'])} stocks): {result['portfolio']}")
        print(f"Final Value: {result['final_value']:.2f} EUR")
        print(f"Annualized Return: {float(result['annualized_return']):.4f}")
        print("Yearly Projections:")
        for year_data in result['projection']:
            print(f"  Year {year_data['year']}: Value={year_data['portfolio_value']:.2f}, "
                  f"Div={year_data['dividend_income']:.2f}, Tax={year_data['total_tax']:.2f}")

if __name__ == "__main__":
    main()