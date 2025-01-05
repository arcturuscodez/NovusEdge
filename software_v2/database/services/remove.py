from options import o
from database.repositories.shareholder import ShareholderRepository

def handle_remove_shareholder(db_conn):
    try:
        shareholder_id = int(o.RemoveShareholder)
    except ValueError:
        print("RemoveShareholder requires a numeric ID.")
        return
    
    repository = ShareholderRepository(db_conn)
    success = repository.delete_shareholder(shareholder_id)
    if success:
        print(f"Successfully removed Shareholder with ID: {shareholder_id}")
    else:
        print(f"Failed to remove Shareholder with ID: {shareholder_id}")