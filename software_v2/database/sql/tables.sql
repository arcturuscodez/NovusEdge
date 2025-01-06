-- Create the SHAREHOLDERS table.
CREATE TABLE IF NOT EXISTS SHAREHOLDERS (
	ID SERIAL PRIMARY KEY,                                                                                  -- Auto-incrementing primary key (Shareholder ID)
	NAME VARCHAR(255) NOT NULL UNIQUE,                                                                      -- Unique and not nullable shareholder names
	OWNERSHIP NUMERIC(5, 2) CHECK (OWNERSHIP > 0 AND OWNERSHIP <=100),                                      -- The amount of ownership in Bearhouse Capital
	INVESTMENT NUMERIC(15, 2) CHECK(INVESTMENT >= 0),                                                       -- The amount invested by the shareholder
	EMAIL VARCHAR(255) NOT NULL UNIQUE,                                                                     -- The shareholders email address
	SHAREHOLDER_STATUS VARCHAR(20) DEFAULT 'active' CHECK (SHAREHOLDER_STATUS IN ('active', 'inactive')),   -- Shareholder status
	CREATED TIMESTAMP DEFAULT CURRENT_TIMESTAMP                                                             -- A timestamp for when the shareholder joined the firm
);

-- Create the FIRM table.
CREATE TABLE IF NOT EXISTS FIRM (
    ID SERIAL PRIMARY KEY,                                                                  -- The id of the firm
    TOTAL_VALUE NUMERIC(20, 2) NOT NULL CHECK(TOTAL_VALUE >= 0),                            -- Total value of the firm (cash reserve + total value of investments)
    TOTAL_VALUE_INVESTMENTS NUMERIC(20, 2) DEFAULT 0 CHECK(TOTAL_VALUE_INVESTMENTS >= 0),   -- Total value in stocks
    CASH_RESERVE NUMERIC(20, 2) DEFAULT 0 CHECK(CASH_RESERVE >= 0),                         -- Firm's cash reserve (unused money)
    NET_PROFIT NUMERIC(20, 2) DEFAULT 0,                                                    -- Net profit of the firm
    NET_LOSS NUMERIC(20, 2) DEFAULT 0,                                                      -- Net loss of the firm
    FIRM_NAME VARCHAR(255) NOT NULL,                                                        -- The name of the firm
    CREATED TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the TRANSACTIONS table.
CREATE TABLE IF NOT EXISTS TRANSACTIONS (
    ID SERIAL PRIMARY KEY,  
    FIRM_ID INT REFERENCES FIRM(ID) ON DELETE CASCADE,                                  -- Links to the FIRM table
    TICKER VARCHAR(10) NOT NULL,                                                        -- Stock ticker (e.g., 'AAPL', 'MSFT')
    SHARES NUMERIC(10, 2) CHECK (SHARES > 0),                                           -- Number of shares involved in the transaction
    PRICE_PER_SHARE NUMERIC(15, 2) CHECK (PRICE_PER_SHARE > 0),                         -- Price per share in the transaction
    TOTAL NUMERIC(20, 2) GENERATED ALWAYS AS (SHARES * PRICE_PER_SHARE) STORED,         -- Calculated total value of the transaction
    TRANSACTION_TYPE VARCHAR(10) NOT NULL CHECK (TRANSACTION_TYPE IN ('buy', 'sell')),  -- Buy or sell transaction
    TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP                                       -- Transaction timestamp
);

-- Create the PORTFOLIO table.
CREATE TABLE IF NOT EXISTS PORTFOLIO (
    FIRM_ID INTEGER,                                                                    -- The ID of the firm which holds the stock
    TICKER TEXT,                                                                        -- The ticker of the stock
    SHARES INTEGER CHECK(SHARES >= 0),                                                  -- Current number of shares held
    AVERAGE_PURCHASE_PRICE REAL CHECK(AVERAGE_PURCHASE_PRICE >= 0),                     -- The average purchase price of shares
    TOTAL_INVESTED REAL CHECK(TOTAL_INVESTED >= 0),                                     -- Total amount invested
    REALIZED_PROFIT_LOSS REAL DEFAULT 0,                                                -- Profit/Loss on sold shares
    CURRENT_PRICE REAL CHECK(CURRENT_PRICE >= 0),                                       -- Current price of ticker
    TOTAL_VALUE REAL GENERATED ALWAYS AS (SHARES * CURRENT_PRICE) STORED,               -- Total value of shares held
    UNREALIZED_PROFIT_LOSS REAL DEFAULT 0,                                              -- Unrealized Profit/Loss on held shares
    DIVIDEND_YIELD_PERCENTAGE REAL DEFAULT 0 CHECK(DIVIDEND_YIELD_PERCENTAGE >= 0),     -- Dividend Yield Percentage
    DIVIDEND_YIELD_AMOUNT REAL DEFAULT 0 CHECK(DIVIDEND_YIELD_AMOUNT >= 0),             -- Dividend Yield Amount (Monthly)
    TOTAL_DIVIDENDS_RECEIVED REAL DEFAULT 0 CHECK(TOTAL_DIVIDENDS_RECEIVED >= 0),       -- Total amount of dividends received from holdings
    LAST_UPDATED TIMESTAMP DEFAULT CURRENT_TIMESTAMP,                                   -- Last updated
    PRIMARY KEY(FIRM_ID, TICKER),
    FOREIGN KEY (FIRM_ID) REFERENCES FIRM(ID) ON DELETE CASCADE
);