from typing import List, Optional
from database.connection import DatabaseConnection
from database.models import FirmModel
from database.queries import Queries

import logging 

logger = logging.getLogger(__name__)

class FirmRepository:
    """Handles all CRUD operations for Firms."""
    
    def __init__(self, db_conn: DatabaseConnection):
        self.db = db_conn

    def add_firm(self, firm: FirmModel) -> str:
        pass
    
    def get_firm_by_id(self, firm_id: int) -> Optional[FirmModel]:
        pass
    
    def get_all_firms(self) -> List[FirmModel]:
        pass
    
    def update_firm(self, firm_id: int, **kwargs) -> bool:
        pass
    
    def update_total_investments(self):
        """
        Update the TOTAL_VALUE_INVESTMENTS column in the FIRM table.
        By summing up the TOTAL_VALUE from the portfolio table.
        """
        try:
            self.db.cursor.execute(
                """ 
                UPDATE FIRM
                SET TOTAL_VALUE_INVESTMENTS = (
                    SELECT COALESCE(SUM(TOTAL_VALUE), 0)
                    FROM PORTFOLIO
                    WHERE PORTFOLIO.FIRM_ID = FIRM.ID
                )
            """
            )
        except Exception as e:
            self.db.connection.rollback()
            logger.error(f'Failed to update total investments: {e}')
            return False
        
    def update_firm_total_value(self, firm_id: int = 1):
        """ 
        Updates the TOTAL_VALUE column in the FIRM table for the given firm_id.
        
        Args:
            firm_id (int): The ID of the firm to update.
        """
        try:
            self.db.cursor.execute(
                """
                SELECT TOTAL_VALUE_INVESTMENTS, CASH_RESERVE
                FROM FIRM
                WHERE ID = %s
                """,
                (firm_id,)
            )
            result = self.db.cursor.fetchone()
            
            if result:
                total_value_investments, cash_reserve = result
                total_value = total_value_investments + cash_reserve
                
                self.db.cursor.execute(
                    """ 
                    UPDATE FIRM
                    SET TOTAL_VALUE = %s
                    WHERE ID = %s
                    """,
                    (total_value, firm_id)
                )
            else:
                print(f'No firm found with ID: {firm_id}')
        except Exception as e:
            self.db.connection.rollback()
            logger.error(f'Failed to update firm total value: {e}')
            return False