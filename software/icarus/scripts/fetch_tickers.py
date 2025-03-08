import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from data.router import DataRouter

class TickerFinder:
    def __init__(self, filename="tickers.csv"):
        self.filename = filename
        self.router = DataRouter()
        self.tickers = self._load_or_fetch_tickers()
    
    def _fetch_tickers(self):
        """Fetch tickers from S&P 500 and Dividend Aristocrats pages"""
        urls = [
            'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies',       # ~503 tickers
            'https://en.wikipedia.org/wiki/S&P_500_Dividend_Aristocrats',     # ~65 tickers
            'https://en.wikipedia.org/wiki/List_of_S%26P_400_companies',      # ~400 tickers
            'https://en.wikipedia.org/wiki/List_of_S%26P_600_companies',      # ~600 tickers
            'https://en.wikipedia.org/wiki/Nasdaq-100',                       # ~100 tickers
            'https://en.wikipedia.org/wiki/Russell_1000_Index'                # ~1000 tickers
        ]
        all_tickers = set()  # Use set to avoid duplicates
        
        for url in urls:
            try:
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                if 'S%26P_500_companies' in url:
                    table = soup.find('table', {'id': 'constituents'})
                    ticker_col = 0
                elif 'Dividend_Aristocrats' in url:
                    table = soup.find('table', {'class': 'wikitable'})
                    ticker_col = 1
                elif 'S%26P_400_companies' in url or 'S%26P_600_companies' in url:
                    table = soup.find('table', {'class': 'wikitable'})
                    ticker_col = 0
                elif 'Nasdaq-100' in url:
                    table = soup.find('table', {'class': 'wikitable'})
                    ticker_col = 1
                elif 'Russell_1000_Index' in url:
                    table = soup.find('table', {'class': 'wikitable'})
                    ticker_col = 0
                else:
                    continue
                
                if not table:
                    print(f"No table found on {url}")
                    continue 

                for row in table.find_all('tr')[1:]:
                    cells = row.find_all('td')
                    if cells and len(cells) > ticker_col:
                        ticker = cells[ticker_col].text.strip().replace('.', '-')
                        all_tickers.add(ticker)

            except Exception as e:
                print(f"Error fetching {url}: {str(e)}")
                continue
        
        return list(all_tickers)
    
    def _load_or_fetch_tickers(self):
        """Load tickers from file if exists, otherwise fetch and save"""
        processed_data = self.router.load_processed_data(self.filename)
        if processed_data is not None:
            print(f"Loaded tickers from processed data: {self.router.get_processed_path(self.filename)}")
            return processed_data['Ticker'].tolist()
        
        raw_data = self.router.load_raw_data(self.filename)
        if raw_data is not None:
            print(f"Loaded tickers from raw data: {self.router.get_raw_path(self.filename)}")
            return raw_data['Ticker'].tolist()

        tickers = self._fetch_tickers()
        df = pd.DataFrame(tickers, columns=['Ticker'])
        df.drop_duplicates(inplace=True)
        
        self.router.save_raw_data(df, self.filename)
        print(f"Saved {len(tickers)} tickers to {self.router.get_raw_path(self.filename)}")
        
        return tickers
    
    def get_tickers(self):
        return self.tickers
    
    def process_tickers(self): # Placeholder
        """Process tickers and save to processed directory"""
        if not self.tickers:
            return False
            
        df = pd.DataFrame(self.tickers, columns=['Ticker'])
        df = df[df['Ticker'].str.match(r'^[A-Z0-9\-]+$')]

        success = self.router.save_processed_data(df, self.filename)
        if success:
            print(f"Processed {len(df)} tickers and saved to {self.router.get_processed_path(self.filename)}")
            
        return success

if __name__ == "__main__":
    ticker_finder = TickerFinder(filename="tickers.csv")
    tickers = ticker_finder.get_tickers()
    print(f"Found {len(tickers)} tickers")
    print("First 10 tickers:", tickers[:10])
    ticker_finder.process_tickers()