from .connection import DatabaseConnection
from .models import BaseModel, GenericModel, ShareholderModel

"""
The database package provides modules for managing database connections,
repositories, and models related to shareholders and other entities.
"""

__version__ = "0.1.5"
__author__ = "Sonny Holman"

__all__ = [
    'DatabaseConnection',
    'BaseModel',
    'GenericModel',
    'ShareholderModel'
]