"""Finance module for Icarus. Includes various financial functions and classes for overall firm operations."""
from decimal import Decimal
from typing import Tuple
from dataclasses import dataclass

@dataclass
class TaxableIncome:
    capital_gains: Decimal # Taxable capital gains (after exemptions)
    dividend_income_domestic: Decimal # Taxable domestic dividends
    dividend_income_foreign: Decimal # Gross foreign dividends (before withholding)
    foreign_tax_paid: Decimal # Foreign tax paid on dividends   
    other_investment_income: Decimal # Other taxable income
    losses: Decimal # Deductible losses

class BearhouseCapitalFeeCalculator:
    """Class for calculating Bearhouse Capital fees."""
    MANAGEMENT_FEE_RATE = Decimal('0.02') # 2% management fee rate
    
    def calculate_management_fee(self, profit: Decimal) -> Decimal:
        """ 
        Given a profit, calculate the management fee.
        """
        profit = max(0, profit)
        return profit * self.MANAGEMENT_FEE_RATE

class FinnishCorporateTaxCalculator:
    """Class for calculating Finnish corporate taxes."""
    CORPORATE_TAX_RATE = Decimal('0.20') # 20% corporate tax rate
    
    def calculate_finnish_tax(self, income: TaxableIncome) -> Tuple[Decimal, Decimal, Decimal]:
        """
        Calculate Finnish corporate taxes for a given taxable income.

        Args:
            income (TaxableIncome): Taxable income for the firm.

        Returns:
            Tuple[Decimal, Decimal, Decimal]: Net Finnish tax and total tax paid.
        """
        total_income = (income.capital_gains + income.dividend_income_domestic + income.dividend_income_foreign + income.other_investment_income)
        
        net_income = max(0, total_income - income.losses)
        
        gross_finnish_tax = net_income * self.CORPORATE_TAX_RATE
        
        max_credit = income.dividend_income_foreign * self.CORPORATE_TAX_RATE
        foreign_tax_credit = min(income.foreign_tax_paid, max_credit)
        
        net_finnish_tax = max(0, gross_finnish_tax - foreign_tax_credit)
        
        total_tax = net_finnish_tax + income.foreign_tax_paid
        
        after_tax_cash = total_income - total_tax
        
        return net_finnish_tax, total_tax, after_tax_cash
    