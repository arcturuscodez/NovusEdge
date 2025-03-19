import os
import sys
from pathlib import Path
import pandas as pd
import time
from decimal import Decimal
import datetime

# Add parent directory to sys.path to import other modules
sys.path.append(str(Path(__file__).parent.parent))
from data.router import DataRouter
from analysis.oracle import Oracle

def main():
    router = DataRouter()
    data = router.load_processed_data("tickers.csv")
    if data is None:
        print("No data found")
        return
    
    # Create an empty list to store enriched data
    enriched_data = []
    
    # Process all tickers
    total_tickers = len(data)
    print(f"Processing {total_tickers} tickers...")
    
    # Track progress
    start_time = time.time()
    success_count = 0
    error_count = 0
    
    for index, row in data.iterrows():
        try:
            ticker = row['Ticker']
            current = index + 1
            
            # Calculate progress statistics
            elapsed = time.time() - start_time
            tickers_per_second = current / elapsed if elapsed > 0 else 0
            percent_complete = (current / total_tickers) * 100
            
            if current > 1:  # Only show estimate after processing at least one ticker
                est_remaining_seconds = (total_tickers - current) / tickers_per_second if tickers_per_second > 0 else 0
                est_completion = datetime.timedelta(seconds=int(est_remaining_seconds))
                
                # Display progress
                print(f"[{current}/{total_tickers}] {percent_complete:.1f}% complete | "
                      f"Processing: {ticker} | "
                      f"Success: {success_count} | Errors: {error_count} | "
                      f"Est. remaining: {est_completion}")
            else:
                print(f"[{current}/{total_tickers}] Processing: {ticker}")
            
            # Create an Oracle instance for this ticker
            oracle = Oracle(ticker)
            
            # Get data from Oracle
            dividend_yield = oracle.get_dividend_yield()
            sector = oracle.get_sector()
            latest_price = oracle.get_latest_closing_price()
            additional_info = oracle.get_additional_info()
            
            # Create enriched row with all the data
            enriched_row = row.copy()
            
            # Handle dividend yield (convert from Decimal to float)
            if dividend_yield is not None:
                try:
                    enriched_row['Dividend_Yield'] = float(dividend_yield)
                except:
                    enriched_row['Dividend_Yield'] = None
            else:
                enriched_row['Dividend_Yield'] = None
                
            enriched_row['Sector'] = sector
            enriched_row['Latest_Price'] = latest_price
            
            # Add additional info if available
            if additional_info and 'info' in additional_info:
                info = additional_info['info']
                enriched_row['Company_Name'] = info.get('shortName')
                enriched_row['Industry'] = info.get('industry')
                enriched_row['Market_Cap'] = info.get('marketCap')
                enriched_row['52Week_High'] = info.get('fiftyTwoWeekHigh')
                enriched_row['52Week_Low'] = info.get('fiftyTwoWeekLow')
                enriched_row['PE_Ratio'] = info.get('trailingPE')
                enriched_row['EPS'] = info.get('trailingEps')
                enriched_row['Beta'] = info.get('beta')
            
            # Add the enriched row to our results
            enriched_data.append(enriched_row)
            success_count += 1
            
            # Save interim results every 50 tickers
            if current % 50 == 0:
                interim_df = pd.DataFrame(enriched_data)
                interim_save_path = os.path.join(os.path.expanduser("~"), "Desktop", "enriched_tickers_interim.csv")
                interim_df.to_csv(interim_save_path, index=False)
                print(f"✅ Interim results saved to {interim_save_path}")
            
            # Add a small delay to avoid rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Error processing ticker {row['Ticker']}: {e}")
            # Still add the original row to maintain the ticker in the output
            enriched_data.append(row)
            error_count += 1

    # Calculate final statistics
    total_time = time.time() - start_time
    avg_time_per_ticker = total_time / total_tickers if total_tickers > 0 else 0
    
    print("\n--- Final Statistics ---")
    print(f"Total tickers processed: {total_tickers}")
    print(f"Successful: {success_count} | Errors: {error_count}")
    print(f"Total processing time: {datetime.timedelta(seconds=int(total_time))}")
    print(f"Average time per ticker: {avg_time_per_ticker:.2f} seconds")

    # Convert to DataFrame and save directly
    enriched_df = pd.DataFrame(enriched_data)
    
    # Save to the processed directory
    save_path = router.get_processed_path("enriched_tickers.csv")
    save_dir = os.path.dirname(save_path)
    
    if not os.path.exists(save_dir):
        print(f"Creating directory: {save_dir}")
        os.makedirs(save_dir, exist_ok=True)
    
    print(f"Saving final data to {save_path}")
    enriched_df.to_csv(save_path, index=False)
    
    # Also save to desktop
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "enriched_tickers_final.csv")
    enriched_df.to_csv(desktop_path, index=False)
    print(f"✅ Final data saved to {save_path}")
    print(f"✅ Backup copy saved to {desktop_path}")

if __name__ == "__main__":
    main()