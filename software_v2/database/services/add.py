from utility import helpers
from options import o
from database.repositories.shareholder import ShareholderRepository
from database.services.update import UpdateService

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

def handle_add_transaction(db_conn):
    parts = o.AddTransaction.split(':')
    if len(parts) != 4:
        print("Invalid format for AddTransaction. Expected format: ticker:shares:pps:transaction_type")
        return
    ticker, shares, pps, transaction_type = parts
    try:
        shares = int(shares)
        pps = float(pps)
        if transaction_type.lower() not in ['buy', 'sell']:
            raise ValueError("Invalid transaction type. Must be 'buy' or 'sell'.")
    except ValueError as e:
        print(e)
        return
    
    service = UpdateService(db_conn)
    success = service.update_portfolio(ticker, shares, pps, transaction_type)
    if success:
        print(f'Successfully added Transaction for {transaction_type} of {shares} shares of {ticker}.')
    else:
        print('Failed to add Transaction.')
    
    