from stocks import StockDataProcessor
from icarus.training import Training
from datetime import datetime, timedelta

def run_test(ticker, days=None, time_steps=60, prediction_days=60):
    # Initialize the StockDataProcessor with the ticker symbol
    processor =  StockDataProcessor(ticker)

    # Fetch historical stock data
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d') if days else '2022-01-01'
    hist_data = processor.fetch_historical_data(start_date, end_date)

    # Transform the data for machine learning
    x, y = processor.transform_data(hist_data, time_steps)

    # Initialize the Training class
    training = Training()

    # Train and evaluate the model
    model, metrics = training.train_and_evaluate(x, y)
    print(f'Trained model: {model}')
    print(f'Metrics: {metrics}')

    # Cross-validate the model
    #cross_val_metrics = training.cross_validate_model(model, x, y)
    #print(f'Cross-Validation Metrics:\n{cross_val_metrics}')

    # Backtest the model
    #backtest_results = training.backtest_model(processor, model, hist_data, time_steps, prediction_days)
    #print(f'Backtest Results:\n{backtest_results}')

    # Predict future stock prices
    recent_data = x[-time_steps:]  # Use the last sequence for prediction
    predictions = training.predict_future_prices(model, recent_data, prediction_days)

    # Plot the predictions
    processor.generate_prediction_plot(hist_data, predictions, prediction_days)

if __name__ == '__main__':
    # Example parameters for testing
    ticker = 'AAPL'
    days = 365  # Last 1 year of data
    time_steps = 60  # Default 60 time steps
    prediction_days = 60  # Default 60 days

    run_test(ticker, days, time_steps, prediction_days)