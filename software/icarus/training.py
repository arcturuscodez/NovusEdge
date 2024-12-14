from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import MinMaxScaler
from .models import Models
import numpy as np

class Training:
    
    def __init__(self, model_type='random_forest'):
        self.models = Models()
        self.scaler = MinMaxScaler()
        self.model_type = model_type
        
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
    
    def transform_data(self, data, time_steps):
        """
        Prepares stock data for machine learning by scaling and creating sequences of historical data.

        Args:
            data (pd.DataFrame): The stock data to be transformed.
            time_steps (int): The number of time steps to look back when creating sequences.

        Returns:
            tuple: Two numpy arrays, x (input data) and y (target data) for machine learning.
        """
        try:
            scaled_data = self.scaler.fit_transform(data[['Close']])
            x, y = [], []

            for i in range(time_steps, len(scaled_data)):
                x.append(scaled_data[i - time_steps:i, 0])
                y.append(scaled_data[i, 0])

            x, y = np.array(x), np.array(y)
            if self.model_type == 'lstm':
                x = x.reshape(x.shape[0], x.shape[1], 1)
            elif self.model_type == 'random_forest':
                x = x.reshape(x.shape[0], x.shape[1]) # Random Forest
            else:
                raise ValueError(f'Invalid model type: {self.model_type}')

            print('Data transformed for machine learning.')
            print(f'x shape: {x.shape}')
            print(f'y shape: {y.shape}')
            return x, y
        except Exception as e:
            print(f'Error transforming data: {e}')
            return None, None
    
    def train_and_evaluate(self, x, y, epochs=10, batch_size=32):
        """ 
        Train and evaluate the model.

        Args:
            x (np.array): Features for training.
            y (np.array): Labels for training.
            epochs (int): Number of epochs for training (only for LSTM).
            batch_size (int): Batch size for training (only for LSTM).

        Returns:
            tuple: The trained model and a dictionary containing the evaluation metrics.
        """
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

        print(f'x_train shape: {x_train.shape}')
        print(f'y_train shape: {y_train.shape}')
        print(f'x_test shape: {x_test.shape}')
        print(f'y_test shape: {y_test.shape}')

        if self.model_type == 'random_forest':
            model = self.models.create_random_forest_model(x_train, y_train, grid_search=False)
        elif self.model_type == 'lstm':
            model = self.models.create_lstm_model((x_train.shape[1], x_train.shape[2]))
            model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size)
        else:
            raise ValueError(f'Invalid model type: {self.model_type}')

        if hasattr(model, 'best_params_'):
            print(f'Best parameters found by grid search: {model.best_params_}')

        y_pred = model.predict(x_test)
        if self.model_type == 'lstm':
            y_pred = self.scaler.inverse_transform(y_pred)
            y_test = self.scaler.inverse_transform(y_test.reshape(-1, 1))

        print(f'y_pred shape: {y_pred.shape}')
        print(f'y_test shape: {y_test.shape}')

        metrics = self.metrics(y_test, y_pred)

        print(f'Evaluation Metrics:\n{metrics}')
        return model, metrics
    
    def predict_future_prices(self, model, data, prediction_days):
        """
        Predict future stock prices using a trained model.
        Also inverses the scaling to get the actual stock prices.    
        
        Args:
            model: The trained model.
            recent_data (np.array): The most recent stock data to base predictions on.
            prediction_days (int): The number of days to predict into the future.
        
        Returns:
            list: A list of predicted stock prices for the specified number of days.
        """
        try:
            predictions = []
            last_sequence = data[-1].reshape(1, -1)
            
            print(f'Initial last_sequence shape: {last_sequence.shape}')
            
            for _ in range(prediction_days):
                next_pred = model.predict(last_sequence)
                predictions.append(next_pred[0])
                last_sequence = np.append(last_sequence[:, 1:], [[next_pred[0]]], axis=1)
                
            predictions = self.scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()
            print('Stock price predictions generated.')
            return predictions
        
        except Exception as e:
            print(f'Error predicting stock prices: {e}')
            return []