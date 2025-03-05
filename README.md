# Software Name

NovusEdge - Investment Firm Management Software

## Description

NovusEdge is an all around investment management software designed for investment firms to manage stock transactions, track portfolio performance, and monitor live market data. It provides users with the ability to execute buy transactions, update portfolio information with real-time stock prices, calculate unrealized profits and losses, and track dividend yields.

The system integrates with a database to store transaction records, portfolio details, and firm financial information. It also leverages external stock data sources to provide live updates on stock prices and dividends. The long-term goal is to enhance the system with machine learning and AI capabilities to simulate, monitor, and provide feedback on the portfolios managed by Bearhouse Capital’s Chief Investment Officer.

### Bearhouse Capital

Bearhouse Capital is an investment firm owned by the developer of NovusEdge. NovusEdge is developed to streamline and optimize Bearhouse Capital's management. The software is currently in development (Version V0.2.2), with several features being tested and refined.

<img src="img\image.png" alt="Project Logo" width="200"/>

### Branch Version

- **V0.2.4** The latest in development version.

## Table of Contents
- [Installation](#installation)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Installation

### Requried Software, Libraries, Etc...

1. Python (v3.10+)
2. PostgreSQL database (v17+)
3. Python Libraries:
  - psycopg2 (PostgreSQL adapter)
  - yfiannce (Yahoo Fianance data)
  - python.dotenv (environment variable management)
  - pandas & numpy (data processing)
  - decimal (precise financial calculations)
4. Anaconda3 (recommended for environment management)

### Setup

1. Clone the repository
2. Create a .env file with the following variables:
  - DB_NAME
  - DB_USER
  - DB_PASS
  - DB_HOST
  - DB_PORT
  - PG_EXE
3. Install dependencies
4. Run the application .\novusedge <command> <subcommand> [options]

**Reminder**

Please review the [LICENSE](LICENSE) file for detailed information on the use of the software.

## Features

- **General**
  - Modular design with clear separation of business logic and data access.
  - Command-line interface options for adding/updating/deleting records.

- **Options & Commands**
  - V0.2.3 introduces a modern subcommand-based CLI interface:

    ```bash
    # Database Server Management
    .\novusedge server start
    .\novusedge server stop
    .\novusedge server status

    # Creating Records
    .\novusedge create shareholder -n "John Doe" -o 10 -i 1000 -e "john@example.com"
    .\novusedge create transaction -t "AAPL" -s 100 -p 150 -a buy
    .\novusedge create firm -n "New Firm"

    # Reading Data
    .\novusedge read shareholders
    .\novusedge read portfolio
    .\novusedge read transactions
    .\novusedge read firm -i 1

    # Updating Records
    .\novusedge update shareholders 1 key=value

    # Deleting Records
    .\novusedge delete shareholders 1

    # Searching for Assets
    .\novusedge search "Apple" --limit 10
    ```

- **Portfolio Management**
  - Transaction Handling: Create buy and sell transactions with automatic portfolio updates
  - Profit/Loss Tracking: Calculate realized and unrealized profit/loss
  - Dividend Tracking: Monitor dividend yields and estimated income
  - Real-time Data: Automatically update portfolio with latest market prices
  - Asset Search: Search for assets across global exchanges

- **Financial Management**
  - Firm Financials: Track firm's cash, assets, expenses, revenue, and liabilities
  - Shareholder Management: Manage shareholder investments, ownership percentages, and withdrawals
  - Fee Calculation: Apply management fees for shareholder profit withdrawals
  - Tax Calculation: Finnish corporate tax calculations for investment income

- **Data Synchronization**
  - Daily portfolio updates with latest market data
  - Automated asset liquidation processing during shareholder withdrawals
  - Comprehensive transaction logging and history

### System Architecture

NovusEdge is built on a modular architecture with clear separation between:

#### Core Components

- **Database Layer** Repository pattern implementation with PostgreSQL
  - Connection pooling for efficient database access
  - Specialized repositories for shareholders, transactions, portfolio, firm, and task data
  - Transactional data integrity with commit/rollback support

- **Business Logic Layer** Services for handling complex operations
  - Create, read, update, and delete operations
  - Withdrawal processing with liquidation planning
  - Automated daily updates

- **Icarus Module** Financial data integration and analysis
  - Market data retrieval from Yahoo Finance
  - Portfolio growth projections
  - Corporate tax calculations
  - Asset data processing


## Contributing

Sonny Holman (Developer)

## License

Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)

Copyright (c) [Bearhouse Capital] [2025]

This work is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License. 
To view a copy of this license, visit https://creativecommons.org/licenses/by-nc/4.0/ or send a 
letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

You are free to:
- Share: copy and redistribute the material in any medium or format
- Adapt: remix, transform, and build upon the material

Under the following terms:
- Attribution: You must give appropriate credit to [Bearhouse Capital], provide a link to the license, 
  and indicate if changes were made. You may do so in any reasonable manner, but not in any way 
  that suggests the licensor endorses you or your use.
- NonCommercial: You may not use the material for commercial purposes.
- No additional restrictions: You may not apply legal terms or technological measures that 
  legally restrict others from doing anything the license permits.

## Contact

Email: sonnyholman@hotmail.com
