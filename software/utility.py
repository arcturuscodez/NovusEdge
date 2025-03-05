import re
from typing import List, Tuple, Union, Any

def format_table_data(column_names: List[str], table_data: List[Tuple[Any, ...]]) -> None:
    """
    Format and print table data with dynamic column widths.
    
    Args:
        column_names (List[str]): List of column names.
        table_data (List[Tuple[Any, ...]]): The rows of the table data.
    """
    if not table_data:
        print("No data to display.")
        return
    print("")
    all_rows = [column_names] + [list(map(str, row)) for row in table_data]
    col_widths = [max(len(str(item)) for item in col) for col in zip(*all_rows)]
    format_str = " | ".join([f"{{:<{width}}}" for width in col_widths])
    
    print(format_str.format(*column_names).upper())
    print("-" * (sum(col_widths) + 3 * (len(col_widths) - 1)))
    
    for row in table_data:
        formatted_row = [str(item) if item is not None else "N/A" for item in row]
        print(format_str.format(*formatted_row))
    print("")

def format_entity_data(entity_data: Union[dict, Any]) -> None:
    """
    Format the entity data and print it to the console.
    
    Args:
        entity_data (Union[dict, Any]): The entity data to format and print.
    """
    if not entity_data:
        print("No data to display.")
        return

    if hasattr(entity_data, '__dataclass_fields__'):
        fields = entity_data.__dataclass_fields__.keys()
        print(f"\n--- {type(entity_data).__name__} (ID: {getattr(entity_data, 'id', 'N/A')}) ---")
        for field in fields:
            value = getattr(entity_data, field, None)
            value_str = str(value) if value is not None else "N/A"
            print(f"{field}: {value_str}")
    elif hasattr(entity_data, 'items'):
        for key, value in entity_data.items():
            print(f"{key}: {value}")
    elif hasattr(entity_data, '__iter__'):
        for key, value in entity_data:
            print(f"{key}: {value}")
    else:
        print(str(entity_data))
    
    print("")

def is_valid_email(email: str) -> bool:
    """
    Check if the email is valid.

    Args:
        email (str): The email to validate.

    Returns:
        bool: True if the email is valid, False otherwise.
    """
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(regex, email) is not None