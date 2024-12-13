    sm = StockDataManager("AAPL")
    hist_data = sm.fetch_historical_data("2020-01-01", "2023-01-01")
    
    # Basic info test
    basic_info = sm.get_basic_info()
    print(basic_info)
    
    # Dividend info test
    dividend_info = sm.get_dividend_info()
    print(dividend_info)

    # Test download data to file_path
    file_path = sm.download_and_save_data("2020-01-01", "2023-01-01", "./")
    print(f'Data saved at: {file_path}')
    
    # Model Training and Prediction
    synthetic_data = sm.generate_synthetic_data(start_price=150, time_steps=3, days=365)
    x, y = sm.transform_data(synthetic_data, time_steps=3)
    
    if x is not None and y is not None:
        model = sm.train_model(x, y)
        predictions = sm.predict_future_prices(model, x[-5:])
        print("Predictions:", predictions)
    
    # Technical Indicators test
    short_data = hist_data.head(15)
    technicals = sm.calclate_technical_indicators(short_data)
    
    # Data validation
    
    valid_data = sm.validate_data(hist_data)
    print(f'Data is valid: {valid_data}')
    
    invalid_data = sm.validate_data(pd.DataFrame())
    print(f'Data is valid: {invalid_data}')
    
    # Synthetic data generation
    small_synthetic_data = sm.generate_synthetic_data(start_price=150, time_steps=3, days=5)
    print(small_synthetic_data)
    
    plotting.plot_data(hist_data, title='Historical Data')
    plotting.plot_data(synthetic_data, title='Synthetic Data')
    
    #future_dates = pd.date_range(start=2024-12-14, periods=len(transformed_predictions))
    
    #if x is not None and y is not None:
        #model = sm.train_model(x, y)
        #predictions = sm.predict_future_prices(model, x[-5:])
        #transformed_predictions = sm.scaler.inverse_transform(predictions.reshape(-1, 1)).flatten()
        #print("Predictions:", predictions)
        #print("Transformed Predictions:", transformed_predictions)
    
    #import matplotlib.pyplot as plt
    #import matplotlib.dates as mdates
    
    #future_dates = pd.date_range(start=2024-12-14, periods=len(transformed_predictions))
    
    #plt.plot(future_dates, transformed_predictions, label='Predicted Prices')
    #plt.plot(future_dates, predictions, label="Predicted Prices")
    #plt.xlabel("Date")
    #plt.ylabel("Price")
    #plt.title("Transformed Predictions")
    
    #plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))  # Year-Month-Day
    #plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))  # Show every day
    
    #plt.legend()
    #plt.grid()
    #plt.show()