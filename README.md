# Software Name

NovusEdge - Investment Firm Management Software

## Description

NovusEdge is an all around investment management software designed for investment firms to manage stock transactions, track portfolio performance, and monitor live market data. It provides users with the ability to execute buy transactions, update portfolio information with real-time stock prices, calculate unrealized profits and losses, and track dividend yields.

The system integrates with a database to store transaction records, portfolio details, and firm financial information. It also leverages external stock data sources to provide live updates on stock prices and dividends. The long-term goal is to enhance the system with machine learning and AI capabilities to simulate, monitor, and provide feedback on the portfolios managed by Bearhouse Capital’s Chief Investment Officer.

### Bearhouse Capital

Bearhouse Capital is an investment firm owned by the developer of NovusEdge. NovusEdge is developed to streamline and optimize Bearhouse Capital's management. The software is currently in development (Version V0.2.2), with several features being tested and refined.

<img src="img\image.png" alt="Project Logo" width="200"/>

### Branch Version

- **V0.2.3** The latest in development version.

## Table of Contents
- [Installation](#installation)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Installation

### Requried Software, Libraries, Etc...

1. Python 3.10
2. psycog2
3. yfinance
4. SQL database

### Environment Setup

1. **Add to System PATH**
   - Open Windows Start menu
   - Search for "Environment Variables"
   - Click "Edit the system environment variables"
   - Click "Environment Variables" button
   - Under "User Variables", find "Path"
   - Click "Edit"
   - Click "New"
   - Add the full path to NovusEdge (e.g., `your-path\NovusEdge`)
   - Click "OK" on all windows

2. **Verify Installation**
   - Open a new PowerShell window
   - Test the command:
   ```powershell
   .\novusedge --help
   ```
   - You should see the help menu with available commands

Note: If the command isn't recognized, try opening a new terminal window to refresh the PATH environment.

## Features

- **General**
  - Modular design with clear separation of business logic and data access.
  - Command-line interface options for adding/updating/deleting records.

- **Options & Commands**
  - V0.2.3 introduces a modern subcommand-based CLI interface:
    ```bash
    # Adding records
    .\novusedge add shareholder --data "name=John:ownership=10:investment=1000:email=john@example.com"
    .\novusedge add transaction --data "ticker=AAPL:shares=100:price=150:type=buy"
    
    # Managing server
    .\novusedge server start
    .\novusedge server stop
    
    # Reading data
    .\novusedge read shareholders
    .\novusedge read portfolio
    
    # Updating records
    .\novusedge update shareholder 1 --data "investment=2000"
    
    # Removing records
    .\novusedge remove shareholders 1
    ```
  - Each command follows a consistent pattern: `.\novusedge <command> <subcommand> [options]`
  - Supports common operations (create, read, update, delete) across all database entities
  - Includes built-in help: `.\novusedge --help` or `.\novusedge <command> --help`
  - Ticker search functionality

- **Database Interaction**
  - Robust integration with PostgreSQL using a connection pool.
  - Repository Pattern implementation in the database layer, supporting CRUD operations across various modules (shareholders, transactions, portfolio, firm, tasks).

- **Icarus**
  - Asset data processing for live market data integration.
  - Functions for inspecting, processing, and cleaning market data.
  - Moving average and daily returns calculations.

- **Asynchronous Updates**
  - Asynchronous portfolio data updates to recalculate assets and dividend yields daily.
  - Automated tasks for updating portfolio information using external data sources.

## Contributing

Sonny Holman (Developer)

## License

This software is proprietary and confidential. Unauthorized use, distribution, or modification for commerical use is prohibited. To use or distribute this software, you must obtain explicit written permission from [Bearhouse Capital] and, where applicable, pay a licensing fee. Contact [sonnyholman@hotmail.com] for inquiries.

## Contact

Email: sonnyholman@hotmail.com
