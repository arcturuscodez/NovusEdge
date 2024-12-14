from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from .models import Models

import numpy as np

class Training:
    
    def __init__(self):
        self.models = Models()
        
    def metrics(self, y_test, y_pred):
        """
        Calculate evaluation metrics.

        Args:
            y_test (np.array): The actual values.
            y_pred (np.array): The predicted values.

        Returns:
            dict: A dictionary containing the evaluation metrics.

        Information:

        The evaluation metrics provide valuable insights into the performance of the model.

        Understanding the Metrics:

        - Mean Absolute Error (MAE): Measures the average magnitude of the errors in a set of predictions, without considering their direction. A lower MAE indicates better performance.
          Example: MAE: 0.007456 means that, on average, the model's predictions are off by approximately 0.007456 units.

        - Mean Squared Error (MSE): Measures the average of the squares of the errors. It gives more weight to larger errors. A lower MSE indicates better performance.
          Example: MSE: 9.747e-05 means that the average squared error is very small, indicating good performance.

        - Root Mean Squared Error (RMSE): The square root of MSE. It provides a measure of the average magnitude of the error.
          Example: RMSE: 0.009873 means that the average magnitude of the error is approximately 0.009873 units.

        - R-squared (R²): Indicates the proportion of the variance in the dependent variable that is predictable from the independent variables. An R² value closer to 1 indicates better performance.
          Example: R²: 0.9908 means that the model explains approximately 99.08% of the variance in the data, indicating very good performance.
        """
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)  
        
        return {
            'MAE': mae,
            'MSE': mse,
            'RMSE': rmse,
            'R2': r2
        }    
        
    def train_and_evaluate(self, x, y):
        """ 
        Train and evaluate the model.
        
        Args:
            x (np.array): Features for training.
            y (np.array): Labels for training.
            
        Returns:
            dict: A dictionary containing the evaulation metrics.
        """
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
        model = self.models.create_random_forest_model(x_train, y_train)
        
        metrics = self.metrics(y_test, model.predict(x_test))    
        
        print(f'Evaluation Metrics:\n{metrics}')
        return model, metrics
    
    def cross_validate_model(self, model, x, y):
        """
        Perform cross-validation on the model.

        Args:
            model (RandomForestRegressor): The trained model.
            x (np.array): Features for cross-validation.
            y (np.array): Labels for cross-validation.

        Returns:
            dict: A dictionary containing the cross-validation scores.
        """
        scores = cross_val_score(model, x, y, cv=5, scoring='neg_mean_absolute_error')
        return {
            'Cross-Validation MAE': -scores.mean(),
            'Cross-Validation Std': scores.std()
        }
            
    def backtest_model(self, processor, model, data, time_steps, prediction_days):
        """
        Backtest the model by making predictions starting from various points in the historical data.

        Args:
            processor (StockDataProcessor): The data processor instance.
            model (RandomForestRegressor): The trained model.
            hist_data (pd.DataFrame): Historical stock data.
            time_steps (int): The number of time steps for prediction.
            prediction_days (int): The number of days to predict into the future.

        Returns:
            dict: A dictionary containing the backtest results.
        """
        results = {}
        for start in range(len(data) - time_steps - prediction_days):
            recent_data = data[start:start + time_steps].values
            true_values = data[start + time_steps:start + time_steps + prediction_days]['Close'].values
            predictions = processor.training.predict_future_prices(model, recent_data, prediction_days)
            metrics = {
                'MAE': mean_absolute_error(true_values, predictions),
                'MSE': mean_squared_error(true_values, predictions),
                'RMSE': np.sqrt(mean_squared_error(true_values, predictions)),
                'R2': r2_score(true_values, predictions)
            }
            results[start] = metrics
        return results
    
    def predict_future_prices(self, model, data, prediction_days):
        """
        Predict future stock prices using a trained Random Forest model.
        
        Args:
            model (RandomForestRegressor): The trained model.
            recent_data (np.array): The most recent stock data to base predictions on.
            prediction_days (int): The number of days to predict into the future.
        
        Returns:
            list: A list of predicted stock prices for the specified number of days.
        """
        try:
            predictions = []
            last_sequence = data[-1].reshape(1, -1)
            
            for _ in range(prediction_days):
                next_pred = model.predict(last_sequence)
                predictions.append(next_pred[0])
                last_sequence = np.append(last_sequence[:, 1:], [[next_pred[0]]], axis=1)
                
            #predictions = scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()
            print('Stock price predictions generated.')
            return predictions
        
        except Exception as e:
            print(f'Error predicting stock prices: {e}')
            return []