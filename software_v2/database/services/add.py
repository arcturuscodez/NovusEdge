from utility import helpers
from options import o
from database.repositories.shareholder import ShareholderRepository

def handle_add_shareholder(db_conn):
    parts = o.AddShareholder.split(':')
    if len(parts) != 4:
        print("Invalid format for AddShareholder. Expected format: name:ownership:investment:email")
        return
    name, ownership, investment, email = parts
    if not helpers.is_valid_email(email):
        print("Invalid email address.")
        return
    try:
        ownership = float(ownership)
        investment = float(investment)
    except ValueError:
        print("Ownership and Investment must be numeric values.")
        return
    
    repository = ShareholderRepository(db_conn)
    shareholder_id = repository.add_shareholder(name, ownership, investment, email)
    if shareholder_id:
        print(f"Successfully added Shareholder with ID: {shareholder_id}")
    else:
        print("Failed to add Shareholder.")
        