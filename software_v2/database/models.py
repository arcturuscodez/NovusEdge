from dataclasses import dataclass
from typing import Optional

@dataclass
class ShareholderModel:
    id: Optional[int]
    name: str
    ownership: float
    investment: float
    email: str
    
@dataclass
class FirmModel:
    id: Optional[int]
    firm_name: str
    total_value: float
    total_investments: float
    cash_reserve: float
    net_profit: float
    net_loss: float
    
@dataclass
class TransactionModel:
    id: Optional[int]
    ticker: str # Stock ticker
    shares: int
    pps: float # Price per share
    firm_id: int
    transaction_type: str # 'buy' or 'sell'
    timestamp: Optional[str]
    
@dataclass
class PortfolioModel:
    id: Optional[int]
    ticker: str
    shares: int
    avg_price: float
    current_price: float
    latest_dividend: float
    portfolio_id: int