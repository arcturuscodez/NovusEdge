# Bearhouse Capital

<img src="software\img\logo.png" alt="Project Logo" width="200"/>

# Software Name

NovusEdge

## Description
Software for the management of investment firm systems, finances, etc...

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

## Features

### Tables

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

## Contributing

Sonny Holman (Main Developer)

## License

All rights reserved.

## Contact

Email: sonnyholman@hotmail.com
