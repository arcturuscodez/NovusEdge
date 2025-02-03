# Software Name

NovusEdge - Investment Firm Management Software

## Description

NovusEdge is an all around investment management software designed for investment firms to manage stock transactions, track portfolio performance, and monitor live market data. It provides users with the ability to execute buy transactions, update portfolio information with real-time stock prices, calculate unrealized profits and losses, and track dividend yields.

The system integrates with a database to store transaction records, portfolio details, and firm financial information. It also leverages external stock data sources to provide live updates on stock prices and dividends. The long-term goal is to enhance the system with machine learning and AI capabilities to simulate, monitor, and provide feedback on the portfolios managed by Bearhouse Capital’s Chief Investment Officer.

### Bearhouse Capital

Bearhouse Capital is an investment firm owned by the developer of NovusEdge. NovusEdge is developed to streamline and optimize Bearhouse Capital's management. The software is currently in development (Version V0.2.2), with several features being tested and refined.

<img src="img\image.png" alt="Project Logo" width="200"/>

### Versions

- **Prior Versions** Prior versions are stored on the developer's computer and are not published to github for public viewing.

- **V0.2.1** is an entirely new method of handling the interaction to the database through the use of the repository pattern which can be further examined through [Database Information Documentation](software/database/info.md).

- **V0.2.2** latest branch and version.

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

## Features

- **General**
  - Modular design with clear separation of business logic and data access.
  - Command-line interface options for adding/updating/deleting records.

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

All rights reserved. Please refer to the LICENSE file for more details on usage and distribution.

## Contact

Email: sonnyholman@hotmail.com
