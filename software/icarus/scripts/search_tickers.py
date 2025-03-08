import yfinance as yf

import logging

logger = logging.getLogger(__name__)

def search_similar_tickers(query: str, limit: int = 10) -> list[dict]:
    """ 
    Search for tickers similar to the provided query string using Yahoo Finance API.
    Args:
        query (str): The query string to search for.
        limit (int): Maximum number of results to return. Default is 10.
    Returns:
        list[dict]: A list of dictionaries containing information:
                    - symbol: The ticker symbol.
                    - name: The name of the company.
                    - exchange: The exchange where the asset is traded.
                    - type: The type of asset (e.g., stock).
                    - score: A relevance score for the search result.
    """
    if not query or len(query) < 2:
        logger.warning('Search query must be at least 2 characters')
        return []
    try:
        logger.info(f'Searching for tickers similar to: {query}')
        search_queries = [
            query,  # Original query
            f"{query}.DE",  # German exchange
            f"{query}.F",   # Frankfurt
            f"{query}.PA",  # Paris
            f"{query}.L",   # London
            f"{query}.TO",  # Toronto
            f"{query}.AX",  # Australia
            f"{query}.MI",  # Milan
            f"{query}.MC"   # Madrid
        ]
        if " " in query:
            search_queries.append(query.replace(" ", ""))
            search_queries.append(query.split(" ")[0])
        search_results = []
        seen_symbols = set()
        for search_query in search_queries:
            if len(search_results) >= limit:
                break
            try:
                ticker_obj = yf.Ticker(search_query)
                info = ticker_obj.info
                if info and 'shortName' in info and 'symbol' in info:
                    symbol = info['symbol']
                    if symbol not in seen_symbols:
                        seen_symbols.add(symbol)
                        search_results.append({
                            'symbol': symbol,
                            'name': info.get('shortName', ''),
                            'exchange': info.get('exchange', ''),
                            'type': info.get('quoteType', ''),
                            'score': 1.0
                        })
            except Exception as e:
                logger.debug(f"Error looking up {search_query}: {e}")
        # If no results, try a broader search using ticker suggestions
        if not search_results:
            try:
                tickers = yf.Tickers(query)
                for symbol, ticker_obj in tickers.tickers.items():
                    if len(search_results) >= limit:
                        break
                    try:
                        info = ticker_obj.info
                        if info and 'shortName' in info:
                            if symbol not in seen_symbols:
                                seen_symbols.add(symbol)
                                search_results.append({
                                    'symbol': symbol,
                                    'name': info.get('shortName', ''),
                                    'exchange': info.get('exchange', ''),
                                    'type': info.get('quoteType', ''),
                                    'score': 0.9
                                })
                    except Exception as e:
                        logger.debug(f'Error processing ticker {symbol}: {e}')
            except Exception as e:
                logger.debug(f"Error during broader search: {e}")
        logger.info(f'Found {len(search_results)} similar tickers for query: {query}')
        
        
        if search_results:
            symbol_width = max(10, max(len(r['symbol']) for r in search_results))
            name_width = max(20, max(len(r['name']) for r in search_results))
            exchange_width = max(10, max(len(r['exchange']) for r in search_results))
            type_width = max(8, max(len(r['type']) for r in search_results))
            print("\nSearch Results:")
            print(f"{'Symbol':<{symbol_width}} {'Name':<{name_width}} {'Exchange':<{exchange_width}} {'Type':<{type_width}}")
            print("-" * (symbol_width + name_width + exchange_width + type_width + 6))
            for result in search_results:
                print(f"{result['symbol']:<{symbol_width}} {result['name']:<{name_width}} {result['exchange']:<{exchange_width}} {result['type']:<{type_width}}")
            print(f"\nFound {len(search_results)} results for '{query}'")
        else:
            print(f"No results found for '{query}'")
            
    except Exception as e:
        logger.error(f'Failed to search for similar tickers: {e}')
        return []