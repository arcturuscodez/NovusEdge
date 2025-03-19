from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
import numpy as np
import random
import logging
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from data.router import DataRouter

logger = logging.getLogger(__name__)

@dataclass
class TickerConfig:
    """Configuration for ticker filtering and portfolio generation"""
    min_dividend_yield: Optional[float] = None
    max_dividend_yield: Optional[float] = None
    min_market_cap: Optional[float] = None
    max_pe_ratio: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_beta: Optional[float] = None
    max_beta: Optional[float] = None
    sectors: Optional[Set[str]] = None
    num_stocks: int = 10
    max_stocks_per_sector: int = 2
    min_eps_growth: Optional[float] = None
    min_roe: Optional[float] = None

class DataLoader:
    """Handles loading and caching of ticker data"""
    def __init__(self, router: DataRouter):
        self.router = router
        self._cache: Dict[str, pd.DataFrame] = {}

    def load_tickers(self, filename: str = "tickers.csv") -> List[str]:
        """Load basic ticker list from CSV"""
        try:
            data = self.router.load_processed_data(filename)
            if data is None or 'Ticker' not in data.columns:
                raise ValueError(f"Invalid ticker data in {filename}")
            return data['Ticker'].tolist()
        except Exception as e:
            logger.error(f"Failed to load tickers: {e}")
            return []

    def load_enriched_data(self, filename: str = "enriched_tickers.csv") -> pd.DataFrame:
        """Load and normalize enriched ticker data"""
        if filename in self._cache:
            return self._cache[filename]

        try:
            
            data = self.router.load_processed_data(filename)
            if data is None:
                
                file_path = Path(__file__).parent.parent.parent / "data" / "processed" / filename
                if not file_path.exists():
                    raise FileNotFoundError(f"Enriched data file not found at {file_path}")
                data = pd.read_csv(file_path)
            
            if data.empty:
                raise ValueError(f"Enriched data file {filename} is empty")
            
            numeric_cols = {
                'Dividend_Yield': float, 'Latest_Price': float, 'Market_Cap': float,
                '52Week_High': float, '52Week_Low': float, 'PE_Ratio': float,
                'EPS': float, 'Beta': float
            }
            
            for col, dtype in numeric_cols.items():
                if col in data.columns:
                    data[col] = pd.to_numeric(data[col], errors='coerce')
            
            data.set_index('Ticker', inplace=True)
            self._cache[filename] = data
            logger.info(f"Loaded enriched data: {len(data)} tickers, {len(data.columns)} attributes")
            return data
            
        except Exception as e:
            logger.error(f"Failed to load enriched data from {filename}: {str(e)}")
            return pd.DataFrame()

class TickerFilter:
    """Filters ticker data based on configuration"""
    @staticmethod
    def filter(data: pd.DataFrame, config: TickerConfig) -> pd.DataFrame:
        """Apply filters to ticker data"""
        df = data.copy()
        
        filters = [
            ('Dividend_Yield', config.min_dividend_yield, '>='),
            ('Dividend_Yield', config.max_dividend_yield, '<='),
            ('Market_Cap', config.min_market_cap, '>='),
            ('PE_Ratio', config.max_pe_ratio, '<=', lambda x: x > 0),
            ('Latest_Price', config.min_price, '>='),
            ('Latest_Price', config.max_price, '<='),
            ('Beta', config.min_beta, '>='),
            ('Beta', config.max_beta, '<=')
        ]
        
        for col, value, op, *extra in filters:
            if value is not None:
                condition = extra[0](df[col]) if extra else True
                df = df[df[col].notna() & (eval(f"df[col] {op} value") & condition)]
        
        if config.sectors:
            df = df[df['Sector'].isin(config.sectors)]
            
        return df

class PortfolioBuilder:
    """Generates portfolios optimized for predicted performance"""
    def __init__(self, data: pd.DataFrame):
        self.data = data.dropna(subset=['Dividend_Yield', 'EPS', 'PE_Ratio', 'Beta', 'Market_Cap'])
        self.required_cols = ['Sector', 'Dividend_Yield', 'EPS', 'PE_Ratio', 'Beta', 'Market_Cap']
        self.optional_cols = ['EPS_Growth', 'ROE', '52Week_Change']

    def build_performance_optimized(self, config: TickerConfig, 
                                  existing_portfolios: List[List[str]] = None) -> List[str]:
        """Generate a portfolio optimized for future performance with minimum size enforcement"""
        if self.data.empty:
            logger.warning("No data available for portfolio generation")
            return []

        df = self.data.copy()
        if config.min_eps_growth and 'EPS_Growth' in df.columns:
            df = df[df['EPS_Growth'] >= config.min_eps_growth]
        if config.min_roe and 'ROE' in df.columns:
            df = df[df['ROE'] >= config.min_roe]

        if len(df) < config.num_stocks:
            logger.warning(f"Insufficient stocks ({len(df)}) after filters, using all available")
            df = self.data.copy()  
        
        excluded = set().union(*existing_portfolios) if existing_portfolios else set()
        available_df = df[~df.index.isin(excluded)].copy()

        
        available_df['Score'] = self._calculate_performance_score(available_df)
        available_df = available_df.sort_values('Score', ascending=False)

        portfolio: List[str] = []
        sector_counts: Dict[str, int] = {}
        available_sectors = available_df['Sector'].unique().tolist()
        random.shuffle(available_sectors)

        for sector in available_sectors:
            sector_df = available_df[available_df['Sector'] == sector]
            available = config.max_stocks_per_sector - sector_counts.get(sector, 0)
            if available > 0 and len(sector_df) > 0:
                top_n = min(5, len(sector_df))
                candidates = sector_df.iloc[:top_n].index.tolist()
                selected = random.sample(candidates, min(available, len(candidates)))
                portfolio.extend(selected)
                sector_counts[sector] = sector_counts.get(sector, 0) + len(selected)

        while len(portfolio) < config.num_stocks:
            remaining = available_df[~available_df.index.isin(portfolio)]
            if remaining.empty:
                logger.warning("Ran out of unique stocks, relaxing exclusion")
                remaining = df[~df.index.isin(portfolio)]
                if remaining.empty:
                    break

            needed = config.num_stocks - len(portfolio)
            extra = remaining.sample(n=min(needed, len(remaining)), random_state=None).index.tolist()
            portfolio.extend(extra)
            
            for ticker in extra:
                sector = df.loc[ticker, 'Sector']
                sector_counts[sector] = sector_counts.get(sector, 0) + 1

        if config.max_beta:
            portfolio = self._adjust_beta(portfolio, config.max_beta, config.num_stocks, available_df)

        return portfolio[:config.num_stocks]

    def _calculate_performance_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate a multi-factor score for performance prediction"""
        weights = {
            'Dividend_Yield': 0.2,
            'EPS': 0.2,
            'PE_Ratio': 0.2,
            'EPS_Growth': 0.2,
            'ROE': 0.2,
            '52Week_Change': 0.2
        }

        score = pd.Series(0, index=df.index)
        available_weights = 0.0

        for metric, weight in weights.items():
            if metric in df.columns:
                if metric == 'PE_Ratio':
                    normalized = self._normalize(1 / df[metric].replace(0, np.nan))
                else:
                    normalized = self._normalize(df[metric])
                score += normalized * weight
                available_weights += weight

        if available_weights < 1.0 and available_weights > 0:
            score = score / available_weights

        return score

    def _normalize(self, series: pd.Series) -> pd.Series:
        """Normalize a series to 0-1 scale"""
        return (series - series.min()) / (series.max() - series.min() + 1e-10)

    def _calculate_portfolio_beta(self, portfolio: List[str]) -> float:
        """Calculate weighted average beta of the portfolio"""
        if not portfolio or 'Beta' not in self.data.columns:
            return 0.0
        weights = self.data.loc[portfolio, 'Market_Cap'] / self.data.loc[portfolio, 'Market_Cap'].sum()
        betas = self.data.loc[portfolio, 'Beta']
        return float(np.sum(weights * betas))

    def _adjust_beta(self, portfolio: List[str], max_beta: float, min_size: int, 
                    available_df: pd.DataFrame) -> List[str]:
        """Adjust portfolio beta while maintaining minimum size"""
        current_beta = self._calculate_portfolio_beta(portfolio)
        df = available_df[~available_df.index.isin(portfolio)].copy()

        while current_beta > max_beta and len(portfolio) > min_size:
            high_beta_stock = self.data.loc[portfolio, 'Beta'].idxmax()
            portfolio.remove(high_beta_stock)
            current_beta = self._calculate_portfolio_beta(portfolio)

        while len(portfolio) < min_size and not df.empty:
            # Add lowest beta stocks to maintain size
            low_beta_stock = df['Beta'].idxmin()
            portfolio.append(low_beta_stock)
            df = df.drop(low_beta_stock)
            current_beta = self._calculate_portfolio_beta(portfolio)

        if len(portfolio) < min_size:
            logger.warning(f"Could only achieve {len(portfolio)} stocks after beta adjustment")
        
        return portfolio

class PortfolioGenerator:
    def __init__(self):
        self.router = DataRouter()
        self.loader = DataLoader(self.router)
        self.filter = TickerFilter()

    def generate_portfolios(self, num_portfolios: int, config: TickerConfig, 
                          strategy: str = 'performance_optimized') -> List[List[str]]:
        """Generate multiple unique portfolios based on configuration and strategy"""
        if num_portfolios < 1 or config.num_stocks < 1:
            raise ValueError("Portfolio and stock counts must be positive")

        enriched_data = self.loader.load_enriched_data()
        if enriched_data.empty:
            raise RuntimeError("No enriched data available - check logs for loading errors")

        filtered_data = self.filter.filter(enriched_data, config)
        if len(filtered_data) < config.num_stocks:
            logger.warning(f"Only {len(filtered_data)} tickers available, may not reach {config.num_stocks}")

        builder = PortfolioBuilder(filtered_data)
        strategies = {
            'performance_optimized': builder.build_performance_optimized
        }
        
        if strategy not in strategies:
            raise ValueError(f"Unknown strategy: {strategy}")

        portfolios = []
        max_attempts = num_portfolios * 3

        for _ in range(max_attempts):
            if len(portfolios) >= num_portfolios:
                break
            new_portfolio = strategies[strategy](config, existing_portfolios=portfolios)
            if len(new_portfolio) < config.num_stocks:
                logger.warning(f"Portfolio only has {len(new_portfolio)} stocks, retrying")
                continue
            if new_portfolio and new_portfolio not in portfolios:
                portfolios.append(new_portfolio)

        if len(portfolios) < num_portfolios:
            logger.warning(f"Generated {len(portfolios)} unique portfolios out of {num_portfolios} requested")

        self._save_portfolios(portfolios)
        return portfolios

    def _save_portfolios(self, portfolios: List[List[str]]) -> None:
        """Save generated portfolios"""
        data = [{"id": i, "tickers": p, "metadata": {}} for i, p in enumerate(portfolios)]
        self.router.save_processed_data(data, "generated_portfolios.json")

if __name__ == "__main__":
    generator = PortfolioGenerator()
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

    try:
        portfolios = generator.generate_portfolios(5, config, strategy='performance_optimized')
        print(f"Generated {len(portfolios)} unique portfolios:")
        for p in portfolios:
            print(f"Portfolio ({len(p)} stocks): {p}")
    except Exception as e:
        print(f"Portfolio generation failed: {str(e)}")