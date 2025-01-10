from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any, Dict
import re

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
    id: Optional[int] = None
    name: str = ""
    ownership: float = 0.0 
    investment: float = 0.0
    email: str = ""
    shareholder_status: Optional[str] = 'active'
    created_at: Optional[datetime] = field(default_factory=datetime.now)
    
@dataclass
class TransactionModel(BaseModel):
    """ 
    Dataclass model to represent a transaction.
    """
    pass

@dataclass
class PortfolioModel(BaseModel):
    """ 
    Dataclass model to represent a portfolio"
    """
    pass

@dataclass
class FirmModel(BaseModel):
    """ 
    Dataclass model to represent a firms data.
    """
    pass