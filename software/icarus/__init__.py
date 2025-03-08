"""
The icarus package provides modules for the management, collection and analysis of financial data.
"""
from icarus.analysis import finance, oracle
#from icarus.config import
from icarus.data import router
# from icarus.models import 
from icarus.scripts import fetch_tickers, search_tickers

__version__ = "0.1.0"
__author__ = "Sonny Holman"

__all__ = [
    'finance',
    'oracle',
    'fetch_tickers',
    'project_portfolio_growth',
    'search_tickers',
    'router'
]