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
class ShareholderModel(BaseModel):
    """
    Dataclass model to represent a shareholder.
    """ 
    id: Optional[int] = None
    name: str = ""
    ownership: float = 0.0 
    investment: float = 0.0
    email: str = ""
    status: Optional[str] = 'active'
    timestamp: Optional[datetime] = field(default_factory=datetime.now)
    """
    def __post_init__(self):
        if self.email and not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            raise ValueError(f"Invalid email format: {self.email}")
        # Ensure ownership is within 0-100%
        if not (0.0 <= self.ownership <= 100.0):
            raise ValueError("Ownership must be between 0.0 and 100.0")
        # Ensure investment is non-negative
        if self.investment < 0.0:
            raise ValueError("Investment cannot be negative")"""