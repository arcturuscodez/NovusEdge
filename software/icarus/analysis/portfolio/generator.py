from decimal import Decimal
from typing import List, Dict, Optional, Any, Callable
from pathlib import Path
import concurrent.futures
import threading
import random
import logging
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from data.router import DataRouter
from analysis.oracle import Oracle

logger = logging.getLogger(__name__)

class PortfolioGenerator:
    """
    Class for generating portfolios based on customizable criteria.
    """

    def __init__(self):
        """Initialize the portfolio generator with a DataRouter."""
        self.router = DataRouter()
        self.criteria = {}
        self.ticker_data = {}

    def load_tickers(self, filename: str = "tickers.csv") -> List[str]:
        """ 
        Load tickers from a CSV using the DataRouter.
        
        Args:
            filename: Name of the CSV file containing tickers.
            
        Returns:
            List of tickers symbols
        """
        data = self.router.load_processed_data(filename)
        if data is None or 'Ticker' not in data.columns:
            logger.error(f"Invalid data in {filename}")
            return []
        
        return data['Ticker'].tolist()
    
    def fetch_ticker_data(self, tickers: List[str], attributes: List[str], sample_size: Optional[int] = None) -> Dict[str, Dict[str, Any]]:
        """Optimize with parallel processing"""
        if sample_size:
            tickers = random.sample(tickers, min(sample_size, len(tickers)))

        results = {}

        cached_data = self.load_ticker_data()
        if cached_data:
            logger.info(f"Using cached data for existing tickers")
            results = cached_data
            
            tickers = [t for t in tickers if t not in results]

        if not tickers:
            return results

        total = len(tickers)
        logger.info(f"Fetching data for {total} tickers...")

        progress_lock = threading.Lock()
        completed = 0

        def process_ticker(ticker):
            nonlocal completed
            try:
                ticker_data = {}
                oracle = Oracle(ticker)

                for attr in attributes:
                    if attr == 'dividend_yield':
                        value = oracle.get_dividend_yield()
                        if value is not None and value > Decimal('0'):
                            ticker_data[attr] = value
                    elif attr == 'price':
                        value = oracle.get_latest_closing_price()
                        if value is not None:
                            ticker_data[attr] = value
                    elif attr == 'sector':
                        value = oracle.get_sector()
                        if value is not None:
                            ticker_data[attr] = value

                with progress_lock:
                    nonlocal completed
                    completed += 1
                    if completed % 10 == 0:
                        logger.info(f"Progress: {completed}/{total} ({(completed/total)*100:.1f}%)")

                if len(ticker_data) == len(attributes):
                    logger.info(f"Fetched data for {ticker}: {ticker_data}")
                    return ticker, ticker_data

            except Exception as e:
                logger.error(f"Error processing {ticker}: {str(e)}")

            return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            futures = {executor.submit(process_ticker, ticker): ticker for ticker in tickers}

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    ticker, data = result
                    results[ticker] = data

        self.ticker_data = results
        self.save_ticker_data()
        return results

    def save_ticker_data(self) -> bool:
        """
        Save ticker data for future use.

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.ticker_data:
            return False
        
        serializable_data = {}
        for ticker, attributes in self.ticker_data.items():
            serializable_data[ticker] = {
                attr: float(value) if isinstance(value, Decimal) else value
                for attr, value in attributes.items()
            }

        return self.router.save_processed_data(serializable_data, "ticker_attributes.json")
    
    def load_ticker_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Load prievously saved ticker data.

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mapping tickers to their attribute values
        """
        data = self.router.load_processed_data("ticker_attributes.json")
        if data is None:
            return {}
        
        processed_data = {}
        for ticker, attributes in data.items():
            processed_data[ticker] = {
                attr: Decimal(str(value)) if attr == 'dividend_yield' else value
                for attr, value in attributes.items()
            }
            
        return processed_data
    
    def add_criterion(self, name: str, weight: float, filter_func: Optional[Callable] = None,
                      sort_key: Optional[Callable] = None, description: str = "") -> None:
        """
        Add a criterion for portfolio generation.
        
        Args:
            name: Name of the criterion
            weight: Weight of this criterion (0-1)
            filter_func: Function to filter tickers (takes ticker data, returns bool)
            sort_key: Function to sort tickers (takes ticker data, returns sortable value)
            description: Description of this criterion
        """
        self.criteria[name] = {
            'weight': weight,
            'filter_func': filter_func,
            'sort_key': sort_key,
            'description': description
        }
        logger.info(f"Added criterion: {name} (weight: {weight})")

    def add_range_criterion(self, name: str, attribute: str, min_value: Optional[float] = None, 
                       max_value: Optional[float] = None, weight: float = 1.0,
                       description: str = "") -> None:
        """
        Add a criterion that filters values within a specific range.

        Args:
            name: Name of the criterion
            attribute: The attribute to check (e.g., 'dividend_yield', 'price')
            min_value: Minimum value (inclusive), or None for no minimum
            max_value: Maximum value (inclusive), or None for no maximum
            weight: Weight of this criterion (0-1)
            description: Description of this criterion
        """
        def range_filter(data):
            if attribute not in data:
                return False

            value = float(data[attribute]) if isinstance(data[attribute], (Decimal, float, int)) else data[attribute]

            if min_value is not None and value < min_value:
                return False
            if max_value is not None and value > max_value:
                return False
            return True

        def range_sort_key(data):
            if attribute not in data:
                return 0

            value = float(data[attribute]) if isinstance(data[attribute], (Decimal, float, int)) else data[attribute]

            if min_value is not None and max_value is not None:
                middle = (min_value + max_value) / 2
                distance = abs(value - middle)
                max_distance = (max_value - min_value) / 2
                return 1 - (distance / max_distance) if max_distance > 0 else 0

            elif min_value is not None:
                return value

            elif max_value is not None:
                return -value

            return 0

        range_description = f"{attribute} "
        if min_value is not None and max_value is not None:
            range_description += f"between {min_value} and {max_value}"
        elif min_value is not None:
            range_description += f">= {min_value}"
        elif max_value is not None:
            range_description += f"<= {max_value}"

        if not description:
            description = range_description

        self.add_criterion(
            name=name,
            weight=weight,
            filter_func=range_filter,
            sort_key=range_sort_key,
            description=description
        )

    def generate_portfolios(self, num_portfolios: int = 10,
                            stocks_per_portfolio: int = 6,
                            min_yield: Optional[float] = None) -> List[List[str]]:
        """
        Generate portfolios based on the defined criteria.
        
        Args:
            num_portfolios: Number of portfolios to generate
            stocks_per_portfolio: Number of stocks per portfolio
            min_yield: Optional minimum dividend yield filter
            
        Returns:
            List of portfolios (each portfolio is a list of tickers)
        """
        if not self.ticker_data:
            self.ticker_data = self.load_ticker_data()

        if not self.ticker_data:
            logger.error("No ticker data available for portfolio generation")
            return []
        
        valid_tickers = list(self.ticker_data.keys())
        if min_yield is not None:
            valid_tickers = [t for t in valid_tickers
                             if 'dividend_yield' in self.ticker_data[t]
                             and float(self.ticker_data[t]['dividend_yield']) >= min_yield]
            
        logger.info(f"Found {len(valid_tickers)} valid tickers after filtering")

        if len(valid_tickers) < stocks_per_portfolio:
            logger.error(f"Not enough valid tickers ({len(valid_tickers)}) to create portfolios of {stocks_per_portfolio} stocks")
            return []
        
        for name, criterion in self.criteria.items():
            if criterion['filter_func']:
                valid_tickers = [t for t in valid_tickers if criterion['filter_func'](self.ticker_data[t])]
        
        portfolios = []

        for i in range(num_portfolios):
            portfolio = self._create_portfolio(valid_tickers, stocks_per_portfolio)
            portfolios.append(portfolio)

        self._save_portfolios(portfolios)

        return portfolios
    
    def _create_portfolio(self, valid_tickers: List[str], stocks_per_portfolio: int) -> List[str]:
        """
        Create a single portfolio based on defined criteria.
        
        Args:
            valid_tickers: List of valid tickers
            stocks_per_portfolio: Number of stocks in the portfolio
            
        Returns:
            List of selected tickers
        """
        candidates = valid_tickers.copy()

        if any(criterion['sort_key'] for criterion in self.criteria.values()):
            candidates.sort(key=lambda ticker: sum(
                criterion['weight'] * criterion['sort_key'](self.ticker_data[ticker])
                for name, criterion in self.criteria.items()
                if criterion['sort_key'] is not None
            ), reverse=True)

        segment_size = max(1, len(candidates) // 3)
        high_segment = candidates[:segment_size]
        mid_segment = candidates[segment_size:2*segment_size]
        low_segment = candidates[2*segment_size:]

        selected = []
        if high_segment:
            selected += random.sample(high_segment, min(2, len(high_segment)))
        if mid_segment:
            selected += random.sample(mid_segment, min(2, len(mid_segment)))
        if low_segment:
            selected += random.sample(low_segment, min(2, len(low_segment)))

        if len(selected) < stocks_per_portfolio:
            remaining = [t for t in candidates if t not in selected]
            if remaining:
                selected += random.sample(remaining, min(stocks_per_portfolio - len(selected), len(remaining)))
                
        random.shuffle(selected)
        selected = selected[:stocks_per_portfolio]
        
        return selected
    
    def _save_portfolios(self, portfolios: List[List[str]]) -> bool:
        """Save portfolios with proper decimal handling"""
        enriched_portfolios = []

        for i, portfolio in enumerate(portfolios):
            
            portfolio_attributes = {}
            for ticker in portfolio:
                if ticker in self.ticker_data:
                    ticker_attrs = {}
                    for attr, value in self.ticker_data[ticker].items():
                        if isinstance(value, Decimal):
                            ticker_attrs[attr] = float(value)
                        else:
                            ticker_attrs[attr] = value
                    portfolio_attributes[ticker] = ticker_attrs

            portfolio_data = {
                "id": i,
                "tickers": portfolio,
                "metadata": {
                    "attributes": portfolio_attributes,
                    "criteria": {name: {'weight': c['weight'], 'description': c['description']} 
                                for name, c in self.criteria.items()}
                }
            }
            enriched_portfolios.append(portfolio_data)

        return self.router.save_processed_data(enriched_portfolios, "generated_portfolios.json")
    
    def add_dividend_yield_range(self, min_yield: Optional[float] = 0.02, 
                           max_yield: Optional[float] = 0.06,
                           weight: float = 1.0) -> None:
        """
        Add a criterion specifically for filtering dividend yields within a range.

        Args:
            min_yield: Minimum dividend yield (default: 2%)
            max_yield: Maximum dividend yield (default: 6%) 
            weight: Weight of this criterion (0-1)
        """
        self.add_range_criterion(
            name='dividend_yield_range',
            attribute='dividend_yield',
            min_value=min_yield,
            max_value=max_yield,
            weight=weight,
            description=f"Dividend yield between {min_yield*100:.1f}% and {max_yield*100:.1f}%"
        )

    def generate_yield_focused_portfolios(self,
                                          num_portfolios: int = 10,
                                          stocks_per_portfolio: int = 8, 
                                          min_yield: float = 0.025) -> List[List[str]]:
        """ 
        Generate yield-focused portfolios (conviencence method).
        
        Args:
            num_portfolios: Number of portfolios to generate
            stocks_per_portfolio: Number of stocks per portfolio
            min_yield: Minimum dividend yield for stocks

        Returns:
            List of portfolios (each portfolio is a list of tickers)
        """
        self.criteria = {}
        
        self.add_criterion(
            name='dividend_yield',
            weight=1.0,
            filter_func=lambda data: 'dividend_yield' in data and float(data['dividend_yield']) >= min_yield,
            sort_key=lambda data: float(data['dividend_yield']),
            description='Dividend yield'
        )
        
        return self.generate_portfolios(
            num_portfolios=num_portfolios,
            stocks_per_portfolio=stocks_per_portfolio,
            min_yield=min_yield
        )