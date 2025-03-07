from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any, Dict

@dataclass
class BaseModel:
    """ 
    A flexible base model that can handle arbitrary attributes.
    """
    def to_dict(self) -> Dict[str, Any]:
        """ 
        Convert the instance attributes to a dictionary.
        """
        return self.__dict__
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """ 
        Create an instance of the model from a dictionary.
        
        Args:
            data (Dict{str, Any}): The data to populate the model.
            
        Returns:
            BaseModel: An instance of the model.
        """    
        return cls(**data)
        
    def __repr__(self) -> str:
        """ 
        Custom string representation for debugging.
        """
        fields = ', '.join(f"{key}={value!r}" for key, value in self.to_dict().items())
        return f"{self.__class__.__name__}({fields})"

@dataclass
class GenericModel(BaseModel):
    """
    A generic model to handle any table's data.
    """
    id: Optional[int]
    __dict__: Dict[str, Any]

@dataclass
class ShareholderModel(BaseModel):
    """
    Dataclass model to represent a shareholder.
    """ 
    id: Optional[int] = None                                                            # Shareholder ID
    name: str = ""                                                                      # Shareholder name
    ownership: float = 0.0                                                              # Shareholder ownership percentage of the firm
    investment: float = 0.0                                                             # Shareholder investment in the firm
    email: str = ""                                                                     # Shareholder email
    shareholder_status: Optional[str] = 'active'                                        # Shareholder status
    created_at: Optional[datetime] = field(default_factory=datetime.now)                # Shareholder creation date
    
@dataclass
class TransactionModel(BaseModel):
    """ 
    Dataclass model to represent a transaction.
    """
    id: Optional[int] = None                                                            # Transaction ID
    ticker: str = ""                                                                    # Asset ticker symbol
    shares: float = 0.0                                                                 # Number of shares or number of asset purchased
    price_per_share: float = 0.0                                                        # Price per share of the asset
    total_value: Optional[float] = None                                                 # Total value of the transaction
    transaction_type: str = ""                                                          # Type of transaction (buy, sell, etc.)
    cost_basis: Optional[float] = None                                                  # Cost basis of the transaction
    realized_profit_loss: Optional[float] = None                                        # Realized profit or loss on the transaction
    transaction_fees: Optional[float] = None                                            # Transaction fees
    portion_of_position: Optional[float] = None                                         # Portion of the position
    notes: Optional[str] = None                                                         # Transaction notes
    created_at: Optional[datetime] = field(default_factory=datetime.now)                # Transaction creation date

@dataclass
class PortfolioModel(BaseModel):
    """ 
    Dataclass model to represent a portfolio
    """
    id: Optional[int] = None                                                            # Portfolio entry ID
    ticker: str = ""                                                                    # Asset ticker symbol
    total_shares: float = 0.0                                                           # Total number of shares of the asset
    total_invested: float = 0.0                                                         # Total amount invested in the asset
    average_purchase_price: float = 0.0                                                 # Average purchase price of the asset
    current_price: Optional[float] = None                                               # Current price of the asset
    total_value: Optional[float] = None                                                 # Total value of currently owned asset shares
    unrealized_profit_loss: Optional[float] = None                                      # Unrealized profit or loss on the asset
    realized_profit_loss: Optional[float] = None                                        # Realized profit or loss on the asset
    dividend_yield: Optional[float] = None                                              # Dividend yield of the asset (percentage)
    dividend_yield_cash: Optional[float] = None                                         # Dividend yield in cash
    created_at: Optional[datetime] = field(default_factory=datetime.now)                # Portfolio entry last updated date

@dataclass
class FirmModel(BaseModel):
    """ 
    Dataclass model to represent a firms financial data.
    """
    id: Optional[int] = None                                                            # Firm ID
    capital: Optional[float] = None                                                     # Firm capital
    assets: float = 0.0                                                                 # Firm assets
    cash: float = 0.0                                                                   # Firm cash
    profit_loss: float = 0.0                                                            # Firm profit or loss
    expenses: float = 0.0                                                               # Firm expenses (Monthly)
    revenue: float = 0.0                                                                # Firm revenue (Monthly)
    liabilities: float = 0.0                                                            # Firm liabilities
    firm_name: str = ""                                                                 # Firm name
    created_at: Optional[datetime] = field(default_factory=datetime.now)                # Firm creation date
    
@dataclass
class TaskModel(BaseModel):
    """
    Dataclass model to represent a task.
    """
    task_name: str = ""                                                                 # Task name
    last_run : Optional[datetime] = None                                                # Last run date