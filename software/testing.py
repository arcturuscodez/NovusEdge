import numpy as np
import pandas as pd

import tensorflow as tf

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import LSTM, Dense, Dropout # type: ignore
from stocks import StocksManager as sm

def load_data(ticker='GME'):
    df = sm.fetch_historical_data(ticker)
    print(df.head())
    print(df.info())
    #quit()
    data = df.filter(['Close']).values
    scaler = MinMaxScaler(feature_range=(0,1))
    scaled_data = scaler.fit_transform(data)
    print(scaled_data)
    return scaled_data, scaler

def create_dataset(data, time_step):
    x, y = [], []
    for i in range(len(data) - time_step - 1):
        x.append(data[i:(i + time_step), 0])
        y.append(data[i + time_step, 0])
    return np.array(x), np.array(y)

time_step = 60
epochs = 100
batch_size = 32

# Preprocess

data, scaler = load_data()

print(data, scaler)

# training and test sets

train_size = int(len(data) * 0.8)
train_data = data[0:train_size, :]
test_data = data[train_size - time_step:, :]

x_train, y_train = create_dataset(train_data, time_step)
x_test, y_test = create_dataset(test_data, time_step)

# Reshape

x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

# Build model

model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1], 1)))
model.add(LSTM(units=50, return_sequences=False))
model.add(Dense(units=25))
model.add(Dense(units=1))

model.compile(optimizer='adam', loss='mean_squared_error')
model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size)

predictions = model.predict(x_test)
predictions = scaler.inverse_transform(predictions)

import matplotlib.pyplot as plt

time = np.arange(0, len(y_test))

plt.figure(figsize=(12,6))
plt.plot(time, y_test, label='Actual Stock Price')
plt.plot(time, predictions, label='Predicted Stock Price')
plt.xlabel('Time')
plt.legend()
plt.show()