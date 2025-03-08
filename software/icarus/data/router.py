import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import shutil
import logging

logger = logging.getLogger(__name__)

class DataRouter:
    """
    A class for routing data to appropriate directories within the Icarus project.
    Handles saving and loading data from raw and processed data directories.
    """
    
    def __init__(self, base_dir=None):
        """
        Initialize the DataRouter with the base directory.
        
        Args:
            base_dir (str, optional): Base directory for data. 
                                      If None, uses the directory where this file is located.
        """
        if base_dir is None:
            self.base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        else:
            self.base_dir = Path(base_dir)

        self.raw_dir = self.base_dir / "raw"
        self.processed_dir = self.base_dir / "processed"

        self._ensure_directories()
        
    def _ensure_directories(self):
        """Ensure that the raw and processed directories exist."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def get_raw_path(self, filename):
        """
        Get the full path to a file in the raw directory.
        
        Args:
            filename (str): Name of the file
            
        Returns:
            Path: Full path to the file in the raw directory
        """
        return self.raw_dir / filename
    
    def get_processed_path(self, filename):
        """
        Get the full path to a file in the processed directory.
        
        Args:
            filename (str): Name of the file
            
        Returns:
            Path: Full path to the file in the processed directory
        """
        return self.processed_dir / filename
    
    def save_raw_data(self, data, filename, format="auto"):
        """
        Save data to the raw directory.
        
        Args:
            data: Data to save (DataFrame, dict, list, etc.)
            filename (str): Name of the file to save
            format (str): Format to save in ("csv", "json", "pickle", "auto")
                          If "auto", infers from filename extension
                          
        Returns:
            bool: True if successful, False otherwise
        """
        return self._save_data(data, filename, self.raw_dir, format)
    
    def save_processed_data(self, data, filename, format="auto"):
        """
        Save data to the processed directory.
        
        Args:
            data: Data to save (DataFrame, dict, list, etc.)
            filename (str): Name of the file to save
            format (str): Format to save in ("csv", "json", "pickle", "auto")
                          If "auto", infers from filename extension
                          
        Returns:
            bool: True if successful, False otherwise
        """
        return self._save_data(data, filename, self.processed_dir, format)
    
    def _save_data(self, data, filename, directory, format="auto"):
        """
        Internal method to save data in the specified directory.
        
        Args:
            data: Data to save
            filename (str): Name of the file
            directory (Path): Directory to save to
            format (str): Format to save in
            
        Returns:
            bool: True if successful, False otherwise
        """
        self._ensure_directories()
        
        if format == "auto":
            _, ext = os.path.splitext(filename)
            if ext:
                format = ext[1:].lower()
            else:
                format = "csv"  # Default format
                filename = f"{filename}.csv"

        filepath = directory / filename
        
        try:
            if isinstance(data, pd.DataFrame):
                if format == "csv":
                    data.to_csv(filepath, index=False)
                elif format == "json":
                    data.to_json(filepath)
                elif format == "pickle":
                    data.to_pickle(filepath)
                else:
                    logger.error(f"Unsupported format '{format}' for DataFrame")
                    return False
            elif isinstance(data, (dict, list)):
                if format == "json":
                    with open(filepath, 'w') as f:
                        json.dump(data, f)
                else:
                    logger.error(f"Format '{format}' not supported for dict/list. Use 'json'")
                    return False
            else:
                logger.error(f"Unsupported data type: {type(data)}")
                return False
            
            logger.info(f"Successfully saved data to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving data to {filepath}: {e}")
            return False
    
    def load_raw_data(self, filename, format="auto"):
        """
        Load data from the raw directory.
        
        Args:
            filename (str): Name of the file to load
            format (str): Format of the file ("csv", "json", "pickle", "auto")
                          If "auto", infers from filename extension
                          
        Returns:
            The loaded data or None if loading failed
        """
        return self._load_data(filename, self.raw_dir, format)
    
    def load_processed_data(self, filename, format="auto"):
        """
        Load data from the processed directory.
        
        Args:
            filename (str): Name of the file to load
            format (str): Format of the file ("csv", "json", "pickle", "auto")
                          If "auto", infers from filename extension
                          
        Returns:
            The loaded data or None if loading failed
        """
        return self._load_data(filename, self.processed_dir, format)
    
    def _load_data(self, filename, directory, format="auto"):
        """
        Internal method to load data from the specified directory.
        
        Args:
            filename (str): Name of the file
            directory (Path): Directory to load from
            format (str): Format of the file
            
        Returns:
            The loaded data or None if loading failed
        """
        if format == "auto":
            _, ext = os.path.splitext(filename)
            if ext:
                format = ext[1:].lower()
            else:
                # If no extension provided, try common formats
                for fmt in ["csv", "json", "pickle"]:
                    if (directory / f"{filename}.{fmt}").exists():
                        filename = f"{filename}.{fmt}"
                        format = fmt
                        break

        filepath = directory / filename
        
        if not filepath.exists():
            logger.error(f"File not found: {filepath}")
            return None
        
        try:
            if format == "csv":
                return pd.read_csv(filepath)
            elif format == "json":
                try:
                    return pd.read_json(filepath)
                except:
                    with open(filepath, 'r') as f:
                        return json.load(f)
            elif format == "pickle":
                return pd.read_pickle(filepath)
            else:
                logger.error(f"Unsupported format: {format}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading data from {filepath}: {e}")
            return None
    
    def move_to_processed(self, filename):
        """
        Move a file from raw to processed directory.
        
        Args:
            filename (str): Name of the file to move
            
        Returns:
            bool: True if successful, False otherwise
        """
        source = self.raw_dir / filename
        destination = self.processed_dir / filename
        
        if not source.exists():
            logger.error(f"Source file not found: {source}")
            return False
        
        try:
            shutil.copy2(source, destination)
            logger.info(f"Successfully moved {filename} from raw to processed")
            return True
        except Exception as e:
            logger.error(f"Error moving {filename}: {e}")
            return False
            
    def list_raw_files(self, pattern=None):
        """
        List files in the raw directory.
        
        Args:
            pattern (str, optional): Glob pattern to filter files
            
        Returns:
            list: List of filenames
        """
        if pattern:
            return [f.name for f in self.raw_dir.glob(pattern)]
        return [f.name for f in self.raw_dir.iterdir() if f.is_file()]
    
    def list_processed_files(self, pattern=None):
        """
        List files in the processed directory.
        
        Args:
            pattern (str, optional): Glob pattern to filter files
            
        Returns:
            list: List of filenames
        """
        if pattern:
            return [f.name for f in self.processed_dir.glob(pattern)]
        return [f.name for f in self.processed_dir.iterdir() if f.is_file()]