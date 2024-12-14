# Bearhouse Capital

<img src="software\img\logo.png" alt="Project Logo" width="200"/>

# Software Name

NovusEdge

## Description

The software being developed is a portfolio management system for an investment firm, designed to manage and track stock transactions, portfolio performance, and live market data. It allows users to execute buy transactions, update portfolio information with live stock prices, calculate unrealized profits and losses, and track dividend yields. The system interacts with a database to store transaction records, portfolio details, and firm financial information, and leverages external stock data sources for real-time price and dividend updates.

The end goal of the software is to use machine learning and artificial intelligence to monitor, simulate and provide feedback on the portfolios provided to the software.

### Version

The current version of the software is -> V0.1.9

## Table of Contents
- [Installation](#installation)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Installation

### Requried Software, Libraries, Etc...

1. Python 3.10
2. NumPy
3. yfinance
4. psycog2
5. Anaconda
6. Cuda

## Features

### Database & Tables

1. All tables are viewable through the use of --ST "tablename".
2. All tables can have their data fetched using the fetch_data method.

#### Shareholders

1. Add shareholders.
2. Remove shareholders.
3. Edit shareholders.

#### Transactions

1. Buy transactions.
2. Sell transactions.

#### Portfolio

1. Transactions update the portfolio table based on selling or buying.
2. The portfolio table updates relevant columns during usage of the software
3. The portfolio table can be retrieved for further use.

#### Firm

1. Updates relevant columns regularly depending on actions occurring with other tables.
    - TOTAL_VALUE
    - TOTAL_VALUE_INVESTMENTS
    - CASH_RESERVE

#### History

Note: Currently unimplemented

### Machine Learning, Artificial Intelligence and Data Science Features

#### Implemented Prediction Methods

1. Random Forest Regression
    
    Currently as of 12/14/2024 the only prediction method available is the random forest regression. 
    It is available inside the /icarus directory. 
    It is primarily used for testing purposes until a more refined method of training and deployment can be provided.

    - Predict future values 
    - Backtest predictions 

## Contributing

Sonny Holman (Developer)

## License

All rights reserved.

## Contact

Email: sonnyholman@hotmail.com
