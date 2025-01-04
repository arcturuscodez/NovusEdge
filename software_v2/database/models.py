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
    ownership: str
    investment: float
    email: str
    shareholder_status: Optional[str]
    created: Optional[datetime] = None
    
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