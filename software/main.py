from database import Database, Shareholder, Firm, Transactions, Portfolio
from sql import queries as q
from options import o
from security import credentials
from stocks import StocksManager

class Software:
    
    def __init__(self):
        """Set up the class for database usage."""
        self.db = credentials.DB
        self.user = credentials.USER
        self.password = credentials.PASSWORD
        self.host = credentials.HOST
        self.port = credentials.PORT
        
        self.run()
    
    def run(self):
        with Database(db=self.db, user=self.user, password=self.password, host=self.host, port=self.port) as db:
            
            sm = Shareholder(db.connection, db.cursor)
            tm = Transactions(db.connection, db.cursor)
            fm = Firm(db.connection, db.cursor)
            pm = Portfolio(db.connection, db.cursor)
            
            if o.AddShareholder:
                parts = o.AddShareholder.split(':')
                sm.shareholder_add(name=parts[0], ownership=int(parts[1]), investment=float(parts[2]), email=parts[3])
            elif o.RemoveShareholder:
                sm.shareholder_remove(int(o.RemoveShareholder))
            elif o.EditShareholder:
                sm.shareholder_edit(o.EditShareholder)
            elif o.BuyStock:
                parts = o.BuyStock.split(':')
                tm.transaction_buy(ticker=parts[0], shares=int(parts[1]), pps=float(parts[2]))
            elif o.SellStock:
                parts = o.SellStock.split(':')
                tm.transaction_sell(ticker=parts[0], shares=int(parts[1]), pps=float(parts[2]))
            elif o.PrintTable:
                db.__fetch__(str(o.PrintTable).upper(), print_data=True)
            elif o.Truncate:
                db.CURSOR.execute(q.Queries.TruncateTableData(table_name=str(o.Truncate).upper()))
            elif o.CheckStock:
                dailydata = StocksManager()
                dailydata.CheckStock(o.CheckStock)
            elif o.InitializeFirmTable:
                fm.initialize_firm('Bearhouse Capital')
            
            pm.live_data()
            
if __name__ == '__main__':
    Software()