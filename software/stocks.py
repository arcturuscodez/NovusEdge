import yfinance as yf

class StocksManager:
    """Class for the management, collection, and analysis of stock data."""
    
    def __init__(self):
        pass
    
    @staticmethod
    def DailyData(ticker):
        """Acquire the daily data of a given stock"""
        stock = yf.Ticker(ticker)

        dividend_data = stock.dividends
        current_price = stock.history(period='1d')['Close'][0]
        
        if not dividend_data.empty:
            quarterly_latest_dividend_amount = dividend_data.iloc[-1]
            annual_latest_dividend_amount = quarterly_latest_dividend_amount * 4
            
            return current_price, annual_latest_dividend_amount
        else:
            print(f'No dividend data available for {ticker}')
            return None, None
        
    @staticmethod
    def CheckStock(ticker):
        """Check a stock to see if it exists in the yahoo finance module"""
        stock = yf.Ticker(str(ticker))
        info = stock.info
        
        if info:
            print(f'Stock: {stock} with ticker: {ticker} exists.')
        else:
            raise ValueError(f"Stock with ticker {ticker} not found.")