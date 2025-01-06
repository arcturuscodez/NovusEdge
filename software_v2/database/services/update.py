from options import o
from database.connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)

class UpdateService:
    """A service for updating various parts of the database."""
    def __init__(self, db_conn: DatabaseConnection):
        self.db_conn = db_conn
        
    def update_portfolio(self, ticker: str, shares: int, pps: float, transaction_type: str, firm_id: int = 1):
        from database.repositories.transactions import TransactionsRepository
        from database.repositories.portfolio import PortfolioRepository
        from database.repositories.firm import FirmRepository

        transactions_repo = TransactionsRepository(self.db_conn)
        portfolio_repo = PortfolioRepository(self.db_conn)
        firm_repo = FirmRepository(self.db_conn)

        try:
            transaction_id = transactions_repo.add_transaction(ticker, shares, pps, transaction_type, firm_id)
            if not transaction_id:
                return False

            if transaction_type.lower() == 'buy':
                portfolio_repo.add_asset(firm_id, ticker, shares)
                #firm_repo.update_cash_reserve(firm_id, -shares * pps)

            elif transaction_type.lower() == 'sell':
                asset = portfolio_repo.get_asset_by_ticker(firm_id, ticker)
                if asset and asset.shares >= shares:
                    portfolio_repo.edit_asset_shares(firm_id, ticker, asset.shares - shares)
                    #firm_repo.update_cash_reserve(firm_id, shares * pps)
                else:
                    transactions_repo.delete_transaction(transaction_id)
                    return False
            return True
        except Exception as e:
            logger.error(f'Error in add_transaction: {e}')
            raise  # Propagate the exception to trigger rollback