mylist = ['KO', 'AAPL', 'MSFT', 'NVDA']

import logging
from retriever import AssetRetriever

def main():
    for ticker in mylist:
        print(ticker)
        print(mylist)
        print(f'Processing ticker: {ticker}')
        retriever = AssetRetriever(ticker)
        
        # Retrieve Latest Closing Price
        latest_close = retriever.get_latest_closing_price()
        if latest_close is not None:
            print(f'Latest Closing Price for {ticker}: {latest_close}')
        else:
            logging.warning(f'Could not retrieve latest closing price for {ticker}')
        
        # Retrieve Dividend Information
        dividends = retriever.get_dividend_info()
        if dividends is not None and not dividends.empty:
            print(f'Dividend Information for {ticker}:\n{dividends}')
        else:
            print(f'No dividend information available for {ticker}')
        
        # Retrieve Additional Information
        additional_info = retriever.get_additional_info()
        if additional_info is not None:
            print(f'Additional Information for {ticker}:')
            print(f"Info: {additional_info['info']}")
            print(f"Splits:\n{additional_info['splits']}")
            print(f"Actions:\n{additional_info['actions']}")
        else:
            logging.warning(f'Could not retrieve additional information for {ticker}')
        
        print('-' * 50)

if __name__ == "__main__":
    main()