from typing import List, Optional
from database.connection import DatabaseConnection
from database.models import ShareholderModel
from database.queries import Queries

import logging

logger = logging.getLogger(__name__)

class ShareholderRepository:
    """Handles all CRUD operations for Shareholders."""
    
    def __init__(self, db_conn: DatabaseConnection):
        self.db = db_conn
        
    def add_shareholder(self, shareholder: ShareholderModel) -> int:
        """
        Adds a new shareholder to the database and returns the new ID.

        Args:
            shareholder (ShareholderModel): The shareholder to add.

        Returns:
            Optional[int]: The ID of the newly added shareholder, or None if failed.
        """
        try:
            query, values = Queries.InsertIntoTableQuery(
                'SHAREHOLDERS',
                ['NAME', 'OWNERSHIP', 'INVESTMENT', 'EMAIL'],
                [shareholder.name, shareholder.ownership, shareholder.investment, shareholder.email]
            )
            self.db.cursor.execute(query, values)
            
            # Update cash reserve.
            
            shareholder_id = self.db.cursor.fetchone()[0]
            self.db.connection.commit()
            logger.info(f"Added Shareholder with ID: {shareholder_id}")
            return shareholder_id
        
        except Exception as e:
            self.db.connection.rollback()
            logger.error(f"Failed to add shareholder: {e}")
            return None
        
    def get_shareholder_by_id(self, shareholder_id: int) -> Optional[ShareholderModel]:
        """
        Retrieves a shareholder by their ID.

        Args:
            shareholder_id (int): The ID of the shareholder to retrieve.

        Returns:
            Optional[ShareholderModel]: The retrieved shareholder, or None if not found.
        """
        try:
            query = Queries.FetchTableDataQuery(
                table_name='SHAREHOLDERS',
                columns=['ID', 'NAME', 'OWNERSHIP', 'INVESTMENT', 'EMAIL'],
                condition_column='id'
            )
            self.db.cursor.execute(query, [shareholder_id])
            row = self.db.cursor.fetchone()
            if row:
                shareholder = ShareholderModel(
                    id=row[0],
                    name=row[1],
                    ownership=row[2],
                    investment=row[3],
                    email=row[4]
                )
                logger.info(f"Retrieved Shareholder: {shareholder}")
                return shareholder
            logger.info(f"No Shareholder found with ID: {shareholder_id}")
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve shareholder: {e}")
            return None
        
    def get_all_shareholders(self) -> List[ShareholderModel]:
        """
        Retrieves all shareholders from the database.

        Returns:
            List[ShareholderModel]: A list of all shareholders.
        """
        shareholders = []
        try:
            query = Queries.FetchTableDataQuery(table_name='shareholders')
            self.db.cursor.execute(query)
            rows = self.db.cursor.fetchall()
            for row in rows:
                shareholder = ShareholderModel(
                    id=row[0],
                    name=row[1],
                    ownership=row[2],
                    investment=row[3],
                    email=row[4]
                )
                shareholders.append(shareholder)
            logger.info(f"Retrieved {len(shareholders)} shareholders.")
            return shareholders
        except Exception as e:
            logger.error(f"Failed to retrieve shareholders: {e}")
            return shareholders
        
    def update_shareholder(self, shareholder_id: int, **kwargs) -> bool:
        """
        Updates a shareholder's details.

        Args:
            shareholder_id (int): The ID of the shareholder to update.
            **kwargs: The fields to update with their new values.

        Returns:
            bool: True if update was successful, False otherwise.
        """
        if not kwargs:
            logger.warning("No fields provided for update.")
            return False
        try:
            columns = list(kwargs.keys())
            values = list(kwargs.values())
            query, updated_values = Queries.UpdateTableDataQuery(
                table_name='shareholders',
                columns=columns,
                values=values,
                condition_column='id',
                condition_value=shareholder_id
            )
            self.db.cursor.execute(query, updated_values)
            self.db.connection.commit()
            logger.info(f"Updated Shareholder ID: {shareholder_id}")
            return True
        except Exception as e:
            self.db.connection.rollback()
            logger.error(f"Failed to update shareholder: {e}")
            return False
        
    def delete_shareholder(self, shareholder_id: int) -> bool:
        """
        Deletes a shareholder from the database.

        Args:
            shareholder_id (int): The ID of the shareholder to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            query, values = Queries.DeleteFromTableQuery(
                table_name='shareholders',
                condition_column='id',
                condition_value=shareholder_id
            )
            self.db.cursor.execute(query, values)
            
            # Update cash reserve.
            
            self.db.connection.commit()
            logger.info(f"Deleted Shareholder ID: {shareholder_id}")
            return True
        except Exception as e:
            self.db.connection.rollback()
            logger.error(f"Failed to delete shareholder: {e}")
            return False