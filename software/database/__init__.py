"""
The database package provides modules for managing database connections,
repositories, and models related to shareholders and other entities.
"""
from .connection import DatabaseConnection

from .models import (
    BaseModel, GenericModel, ShareholderModel, 
    TransactionModel, PortfolioModel, FirmModel, TaskModel
)

from .repositories.shareholder import ShareholderRepository
from .repositories.transaction import TransactionRepository
from .repositories.portfolio import PortfolioRepository
from .repositories.firm import FirmRepository
from .repositories.task import TaskRepository

__version__ = "0.3.0"
__author__ = "Sonny Holman"

__all__ = [
    'DatabaseConnection',
    'BaseModel',
    'GenericModel',
    'ShareholderModel',
    'TransactionModel',
    'PortfolioModel',
    'FirmModel',
    'TaskModel',
    'ShareholderRepository',
    'TransactionRepository',
    'PortfolioRepository',
    'FirmRepository',
    'TaskRepository'
]