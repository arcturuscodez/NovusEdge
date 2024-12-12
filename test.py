import matplotlib.pyplot as plt
import numpy as np

# Example: Actual and predicted stock prices
actual_prices = [100, 105, 110, 115, 120]  # Replace with actual stock price data
predicted_prices = [98, 104, 109, 114, 119]  # Replace with predicted stock prices

# Debug: Check values
print("Actual prices:", actual_prices)
print("Predicted prices:", predicted_prices)

# Make sure no zero values are accidentally set for actual prices
if all(value == 0 for value in actual_prices):
    print("Warning: All actual stock prices are zero!")

# Plotting
plt.plot(actual_prices, label='Actual Stock Price')
plt.plot(predicted_prices, label='Predicted Stock Price', linestyle='--')
plt.xlabel('Time')
plt.ylabel('Stock Price')
plt.legend()
plt.title('Stock Price Prediction')
plt.show()
