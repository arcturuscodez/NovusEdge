from typing import List, Optional
from database.repositories.base import BaseRepository
from database.models import TaskModel

import logging

logger = logging.getLogger(__name__)

class TaskRepository(BaseRepository):
    """Repository for task-specific operations."""
    
    def __init__(self, db_conn):
        """Initialize the repository with the Task model."""
        super().__init__(db_conn, table_name='task_metadata', model=TaskModel)
    
    def create_task(self, task_name: str) -> Optional[int]:
        """ 
        Add a new task to the database.
        
        Args:
            task_name (str): Name of the task.
        
        Returns:
            Optional[int]: The ID of the newly added task, or None if failed.
        """
        try:
            new_task = TaskModel(
                task_name=task_name
            )
            return super().create(new_task)

        except Exception as e:
            logger.error(f'Failed to add task: {e}')
            return None
        
    def delete_task(self, task_name: int) -> bool:
        """
        Delete a task by task_name.

        Args:
            task_name (str): The name of the task to delete.
        """
        return super().delete(task_name)
    
    def update_task(self, task_name: str, **kwargs: dict) -> bool:
        """ 
        Update a task's information.
        
        Args:
            task_name (str): The name of the task to update.
            kwargs (dict): The updated information for the task.
        """
        return super().update(task_name, **kwargs)
    
    def get_task_by_name(self, task_name: str) -> Optional[TaskModel]:
        """
        Get a task by its name.
        
        Args:
            task_name (str): The name of the task to retrieve.
        
        Returns:
            Optional[TaskModel]: The task model if found, None otherwise.
        """
        return super().get_entity(task_name)