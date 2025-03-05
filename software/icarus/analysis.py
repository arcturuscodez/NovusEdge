from finance import FinnishCorporateTaxCalculator, TaxableIncome
from decimal import Decimal

def project_portfolio_growth(tax_calculator: FinnishCorporateTaxCalculator,
                             initial_value: Decimal,
                             dividend_yield: Decimal,
                             foreign_withholding_rate: Decimal,
                             years: int,
                             dividend_growth_rate: Decimal = Decimal('0')) -> list[dict]:
    """ 
    Project portfolio value and taxes over multiple years with reinvestment of after-tax dividends.
    
    Args:
        tax_calculator: Instance of FinnishCorporateTaxCalculator.
        initial_value: Starting portfolio value in euros.
        dividend_yield: Annual dividend yield as a decimal. (e.g, 0.03 for 3%)
        foreign_withholding_rate: Foreign withholding tax rate on dividends. (e.g., 0.15 for 15%)
        years: Number of years to project.
        dividend_growth_rate: Annual dividend growth rate as a decimal. (e.g., 0.02 for 2%)
        
    Returns:
        List of dictionaries with yearly results.
        - year: Year number.
        - portfolio_value: Portfolio value in euros.
        - dividend_income: Dividend income in euros.
        - finnish_tax: Finnish corporate tax in euros.
        - total_tax: Total tax in euros (Finnish + foreign) for the year.
    """
    results = []
    portfolio_value = initial_value
    
    for year in range(years + 1):
        if year == 0:
            # Year 0: Initial portfolio value, no income or taxes
            results.append({
                "year": year,
                "portfolio_value": portfolio_value,
                "dividend_income": Decimal('0'),
                "finnish_tax": Decimal('0'),
                "total_tax": Decimal('0'),
                "after_tax_cash": Decimal('0')
            })
            continue
        
        div_yield = dividend_yield * (1 + dividend_growth_rate) ** (year - 1)
        dividend_income = portfolio_value * div_yield
        foreign_tax = dividend_income * foreign_withholding_rate
        
        # Create TaxableIncome object for the year.
        income = TaxableIncome(
            capital_gains=Decimal('0'),
            dividend_income_domestic=Decimal('0'),
            dividend_income_foreign=dividend_income,
            foreign_tax_paid=foreign_tax,
            other_investment_income=Decimal('0'),
            losses=Decimal('0')
        )
        
        finnish_tax, total_tax, after_tax_cash = tax_calculator.calculate_finnish_tax(income)
        
        portfolio_value += after_tax_cash
        
        results.append({
            "year": year,
            "portfolio_value": portfolio_value,
            "dividend_income": dividend_income,
            "finnish_tax": finnish_tax,
            "total_tax": total_tax,
            "after_tax_cash": after_tax_cash
        })
        
    return results