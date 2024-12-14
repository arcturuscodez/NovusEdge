from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from tensorflow.keras.models import Sequential  # type: ignore
from tensorflow.keras.layers import Dense, LSTM # type: ignore
import json

class Models:
    
    def __init__(self):
        pass
    
    def save_best_params(params, filename='best_params.json'):
        with open(filename, 'w') as f:
            json.dump(params, f)

    def load_best_params(filename='best_params.json'):
        with open(filename, 'r') as f:
            return json.load(f)
    
    def add_grid_search(self, model, x_train, y_train):
        """Adds a grid search for hyperparameter tuning."""
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [5, 10, 20, 50, 100],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=3, n_jobs=-1, verbose=2)
        grid_search.fit(x_train, y_train)
        return grid_search    
    
    def create_random_forest_model(self, x_train, y_train, grid_search=False):
        """
        Create and train a Random Forest model with hyperparameter tuning.
        
        Args:
            x_train (np.array): Training data features.
            y_train (np.array): Training data labels.
            grid_search (bool): Whether to perform grid search for hyperparameter tuning.
        
        Returns:
            RandomForestRegressor: The trained Random Forest model.
        """
        if grid_search:
            model = RandomForestRegressor(random_state=42)
            grid_search_model = self.add_grid_search(model, x_train, y_train)
            return grid_search_model
        else:
            model = RandomForestRegressor(max_depth=10, min_samples_leaf=1, n_estimators=200, random_state=42)
            model.fit(x_train, y_train)
            return model
    
    def create_lstm_model(self, input_shape):
        """
        Create and compile an LSTM model.
        
        Args:
            input_shape (tuple): Shape of the input data (time_steps, features).
        
        Returns:
            Sequential: The compiled LSTM model.
        """
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=input_shape),
            LSTM(50),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model