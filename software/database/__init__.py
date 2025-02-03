from .connection import DatabaseConnection

from .models import BaseModel, GenericModel, ShareholderModel, TransactionModel, PortfolioModel, FirmModel, TaskModel

from .repositories.shareholder import ShareholderRepository
from .repositories.transaction import TransactionRepository
from .repositories.portfolio import PortfolioRepository
from .repositories.firm import FirmRepository
from .repositories.task import TaskRepository

"""
The database package provides modules for managing database connections,
repositories, and models related to shareholders and other entities.
"""

__version__ = "0.2.5"
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