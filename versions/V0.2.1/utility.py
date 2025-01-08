import re

def FormatTableData(ColumnName, TableData):
    """
    Format and print table data with dynamic column widths.
    Args:
    - ColumnName (list): List of column names.
    - TableData (list of tuples): The rows of the table data.
    """
    if not TableData:
        print("No data to display.")
        return
    all_rows = [ColumnName] + [list(map(str, row)) for row in TableData]
    col_widths = [max(len(str(item)) for item in col) for col in zip(*all_rows)]
    format_str = " | ".join([f"{{:<{width}}}" for width in col_widths])
    print(format_str.format(*ColumnName).upper())
    print("-" * (sum(col_widths) + 3 * (len(col_widths) - 1)))
    for row in TableData:
        formatted_row = [str(item) if item is not None else "N/A" for item in row]
        print(format_str.format(*formatted_row))
    
    print(f"\n{len(TableData)} rows displayed.")
    
def is_valid_email(email: str) -> bool:
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(regex, email) is not None