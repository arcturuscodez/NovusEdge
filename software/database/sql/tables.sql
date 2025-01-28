-- Tables

-- Create the SHAREHOLDERS table.
CREATE TABLE IF NOT EXISTS SHAREHOLDERS (
    ID SERIAL PRIMARY KEY,
    NAME VARCHAR(255) NOT NULL UNIQUE,
    OWNERSHIP NUMERIC(5, 2) CHECK (OWNERSHIP > 0 AND OWNERSHIP <=100),
    INVESTMENT NUMERIC(15, 2) CHECK (INVESTMENT >= 0),
    EMAIL VARCHAR(255) NOT NULL UNIQUE,
    SHAREHOLDER_STATUS VARCHAR(20) DEFAULT 'active' CHECK (SHAREHOLDER_STATUS IN ('active', 'inactive')),
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the TRANSACTIONS table.
CREATE TABLE IF NOT EXISTS TRANSACTIONS (
    ID SERIAL PRIMARY KEY,
    TICKER VARCHAR(10) NOT NULL,
    SHARES NUMERIC(10, 2) CHECK (SHARES > 0),
    PRICE_PER_SHARE NUMERIC(15, 2) CHECK (PRICE_PER_SHARE > 0),
    TOTAL_VALUE NUMERIC(20, 2) GENERATED ALWAYS AS (SHARES * PRICE_PER_SHARE) STORED,
    TRANSACTION_TYPE VARCHAR(10) NOT NULL CHECK (TRANSACTION_TYPE IN ('buy', 'sell')),
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the PORTFOLIO table.
CREATE TABLE IF NOT EXISTS PORTFOLIO (
    ID SERIAL PRIMARY KEY,                                                                                                      -- Entry ID
    TICKER VARCHAR(10) NOT NULL UNIQUE,                                                                                         -- Unique asset ticker
    TOTAL_SHARES NUMERIC(10, 2) CHECK (TOTAL_SHARES > 0),                                                                       -- Total owned shares of the asset
    TOTAL_INVESTED NUMERIC(20, 2) CHECK (TOTAL_INVESTED >= 0),                                                                  -- The total invested in the asset
    CURRENT_PRICE NUMERIC(15, 2) CHECK (CURRENT_PRICE >= 0),                                                                    -- The current price of 1 of the asset
    TOTAL_VALUE NUMERIC(20, 2) GENERATED ALWAYS AS (TOTAL_SHARES * CURRENT_PRICE) STORED,                                       -- The total value of all owned shares of the asset
    UNREALIZED_PROFIT_LOSS NUMERIC(20, 2) GENERATED ALWAYS AS (TOTAL_SHARES * CURRENT_PRICE - TOTAL_INVESTED) STORED,           -- The unrealized profit or loss of the asset
    REALIZED_PROFIT_LOSS NUMERIC(20, 2) DEFAULT 0,                                                                              -- The realized profit or loss of the asset
    DIVIDEND_YIELD REAL DEFAULT 0 CHECK (DIVIDEND_YIELD >= 0),                                                                  -- The dividend yield of the asset (percentage)
    DIVIDEND_YIELD_CASH NUMERIC(20, 2) GENERATED ALWAYS AS ((DIVIDEND_YIELD / 100) * (TOTAL_SHARES * CURRENT_PRICE)) STORED,    -- The dividend yield in cash value
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP                                                                              -- The last time the asset was updated       
);

-- Create the FIRM table.
CREATE TABLE IF NOT EXISTS FIRM (
    ID SERIAL PRIMARY KEY,                                                                                                      -- Entry ID
    CAPITAL NUMERIC(20, 2) GENERATED ALWAYS AS (ASSETS + CASH) STORED,                                                                                            -- The total cumulative capital of the firm
    ASSETS NUMERIC(20, 2) DEFAULT 0,                                                                                            -- The total cumulative invested capital of the firm in assets
    CASH NUMERIC(20, 2) DEFAULT 0,                                                                                              -- The total cash reserve of the firm
    PROFIT_LOSS NUMERIC(20, 2) DEFAULT 0,                                                                                       -- The total profit or loss of the firm
    EXPENSES NUMERIC(20, 2) DEFAULT 0,                                                                                          -- The total expenses of the firm
    REVENUE NUMERIC(20, 2) DEFAULT 0,                                                                                           -- The total revenue of the firm
    LIABILITIES NUMERIC(20, 2) DEFAULT 0,                                                                                       -- The total liabilities of the firm
    FIRM_NAME VARCHAR(255) NOT NULL UNIQUE,                                                                                     -- The name of the firm
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP                                                                              -- The time the firm was created
);

CREATE TABLE IF NOT EXISTS TASK_METADATA (
    TASK_NAME TEXT PRIMARY KEY,
    LAST_RUN TIMESTAMP
);