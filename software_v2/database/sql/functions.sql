-- FUNCTIONS

-- UPDATE PORTFOLIO AFTER BUY
	
CREATE OR REPLACE FUNCTION update_average_purchase_price()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if the transaction is a buy
    IF (NEW.transaction_type = 'buy') THEN
        -- If the stock already exists in the portfolio, update the average purchase price
        UPDATE PORTFOLIO
        SET shares = shares + NEW.shares,
            total_invested = total_invested + (NEW.shares * NEW.price_per_share),
            average_purchase_price = (total_invested + (NEW.shares * NEW.price_per_share)) / (shares + NEW.shares)
        WHERE ticker = NEW.ticker AND firm_id = NEW.firm_id;

        -- If the stock does not exist, insert a new row in the portfolio table
        INSERT INTO PORTFOLIO (firm_id, ticker, shares, total_invested, average_purchase_price)
        SELECT NEW.firm_id, NEW.ticker, NEW.shares, NEW.shares * NEW.price_per_share, NEW.price_per_share
        WHERE NOT EXISTS (SELECT 1 FROM PORTFOLIO WHERE ticker = NEW.ticker AND firm_id = NEW.firm_id);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- UPDATE PORTFOLIO AFTER SELL

CREATE OR REPLACE FUNCTION update_portfolio_after_sell()
RETURNS TRIGGER AS $$
BEGIN
    -- If the transaction is a sell, update the number of shares in the portfolio
    UPDATE PORTFOLIO
    SET shares = shares - NEW.shares,
        total_invested = total_invested - (NEW.shares * average_purchase_price)
    WHERE ticker = NEW.ticker AND firm_id = NEW.firm_id;

    -- If all shares are sold, delete the row from the portfolio
    DELETE FROM PORTFOLIO
    WHERE ticker = NEW.ticker AND firm_id = NEW.firm_id AND shares = 0;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- UPDATE PORTFOLIO AFTER LIVE UPDATE

CREATE OR REPLACE FUNCTION update_unrealized_profit_loss()
RETURNS TRIGGER AS $$
BEGIN
    NEW.UNREALIZED_PROFIT_LOSS := NEW.SHARES * NEW.CURRENT_PRICE - NEW.TOTAL_INVESTED;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- TRIGGERS

	-- AFTER BUY TRIGGER
CREATE TRIGGER after_buy_transaction
AFTER INSERT ON TRANSACTIONS
FOR EACH ROW
WHEN (NEW.TRANSACTION_TYPE = 'buy')
EXECUTE FUNCTION update_average_purchase_price();

	-- AFTER SELL TRIGGER

CREATE TRIGGER after_sell_transaction
AFTER INSERT ON TRANSACTIONS
FOR EACH ROW
WHEN (NEW.transaction_type = 'sell')
EXECUTE FUNCTION update_portfolio_after_sell();

	-- AFTER LIVE UPDATE TRIGGER

CREATE TRIGGER after_live_update
BEFORE UPDATE ON PORTFOLIO
FOR EACH ROW
EXECUTE FUNCTION update_unrealized_profit_loss()
		
