from database import Database, Shareholder, Firm, Transactions, Portfolio, History
from sql import queries as q
from options import o
from security import credentials
from psycopg2 import OperationalError

from datetime import datetime, timedelta

class NovusEdge:
    
    def __init__(self):
        """Set up the class for software usage."""
        self.db = credentials.DB
        self.user = credentials.USER
        self.password = credentials.PASSWORD
        self.host = credentials.HOST
        self.port = credentials.PORT
        self.pg_exe = credentials.PG_EXE_PATH
        
        self.run()
        
    def run(self):
        try:
            with Database(db=self.db, user=self.user, password=self.password, host=self.host, port=self.port, pg_exe=self.pg_exe) as db:
                
                sm = Shareholder(db.connection, db.cursor)
                tm = Transactions(db.connection, db.cursor)
                fm = Firm(db.connection, db.cursor)
                pm = Portfolio(db.connection, db.cursor)
                
                if o.PrintTable:
                    db.fetch_data(str(o.PrintTable).upper(), print_data=True)
                elif o.AddShareholder:
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
                elif o.Truncate:
                    db.cursor.execute(q.Queries.TruncateTableDataQuery(table_name=str(o.Truncate).upper()))
                elif o.InitializeFirmTable:
                    fm.create_firm_rows('Bearhouse Capital')
                elif o.plotdata:
                    from stocks_v2 import StockDataManager
                    manager = StockDataManager(str(o.plotdata).upper())
                    end_date = datetime.today()
                    start_date = end_date - timedelta(days=5 * 365)
                    hist_data = manager.fetch_historical_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
                    
                    if hist_data.empty:
                        print('No historical data found. Exiting')
                        exit()
                    
                    time_steps = 60
                    
                    x, y = manager.transform_data(hist_data, time_steps)
                    if x is not None and y is not None:
                        model = manager.train_model(x, y)
                    if model: 
                        predictions = manager.random_forest_regression_prediction(time_steps, model, x, prediction_days=60)
                        manager.plot_stock_predictions(hist_data, predictions, end_date, prediction_days=60)
                                    
                pm.portfolio_live_data()
                fm.update_total_investments()
                fm.update_firm_total_value()
        
        except OperationalError as e:
            print(f'Failed to connect to the database: {e}')
        except Exception as e:
            print(f'An unexepected error occured: {e}')

if __name__ == '__main__':
    NovusEdge()