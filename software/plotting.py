import matplotlib.pyplot as plt

def plot_data(data, title="Stock Data"):
    """Plots stock closing prices and indicators."""
    try:
        plt.figure(figsize=(10, 6))
        plt.plot(data['Close'], label='Close Price')
        if 'SMA_20' in data.columns:
            plt.plot(data['SMA_20'], label='SMA 20')
        if 'EMA_20' in data.columns:
            plt.plot(data['EMA_20'], label='EMA 20')
        plt.title(title)
        plt.legend()
        plt.show()
    except Exception as e:
        print(f'Error plotting data: {e}')