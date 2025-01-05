from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any, Dict

@dataclass
class BaseModel:
    """
    A flexible base model that can handle arbitrary attributes.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the model with any number of positional and keyword arguments.
        Maps positional arguments to attribute names based on table schema.
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the instance attributes to a dictionary.
        """
        return self.__dict__

    def __repr__(self) -> str:
        """
        Custom string representation for debugging.
        """
        fields = ', '.join(f"{key}={value!r}" for key, value in self.to_dict().items())
        return f"{self.__class__.__name__}({fields})"

@dataclass
class ShareholderModel(BaseModel):
    """
    Model representing a shareholder.
    """
    id: Optional[int]
    name: str
    ownership: float
    investment: float
    email: str
    shareholder_status: Optional[str]
    created: Optional[datetime] = None

@dataclass
class TransactionsModel:
    """ 
    Model representing an asset transaction.
    """
    id: Optional[int]
    firm_id: Optional[int]
    ticker: str # Stock ticker
    shares: int # Number of shares
    price_per_share: float # pps 
    total: float # total cost
    transaction_type: str # 'buy' or 'sell'
    timestamp: Optional[datetime] = None
    
@dataclass
class FirmModel:
    """ 
    Model representing a firm table.
    """
    id: Optional[int]
    total_value: float
    total_value_investments: float
    cash_reserve: float
    net_profit: float
    net_loss: float
    created: Optional[datetime] = None
    
@dataclass
class PortfolioModel:
    """ 
    Model representing a portfolio of assets.
    """
    firm_id: int
    ticker: str
    shares: int
    average_purchase_price: float
    total_invested: float
    realized_profit_loss: float
    current_price: float
    total_value: float
    unrealized_profit_loss: float
    dividend_yield_percentage: float
    dividend_yield_amount: float
    total_dividends_received: float
    last_updated: Optional[datetime] = None
    