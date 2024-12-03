import yfinance as yf
import time

def get_stock_data(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period='1m', interval='1m')
    current_price = data['Close'].iloc[-1]
    return current_price

def get_live_price(symbol):
    stock = yf.Ticker(symbol)
    live_price = stock.info['regularMarketPrice']  # Fetch real-time market price
    return live_price

def monitor_stock(symbol):
    print(f'Monitoring stock data for symbol {symbol}...\n')
    try:
        while True:
            price = get_live_price(symbol)
            print(f"Current price for {symbol}: ${price:.2f}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

symbol = 'AAPL'
monitor_stock(symbol)