.. MyMT5 documentation master file

MyMT5 Documentation
===================

Welcome to MyMT5's documentation! MyMT5 is a comprehensive Python library for interacting with MetaTrader 5 terminal.

.. image:: https://img.shields.io/badge/python-3.8%2B-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python Version

.. image:: https://img.shields.io/badge/license-MIT-green.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License

Features
--------

* **Connection Management**: Robust connection handling with automatic reconnection
* **Multi-Account Support**: Seamlessly switch between multiple accounts
* **Trading Operations**: Complete trading API for market and pending orders
* **Risk Management**: Position sizing, risk calculations, portfolio analytics
* **Market Data**: Real-time quotes, historical bars, tick data
* **Historical Analysis**: Performance metrics, trade analysis, reporting
* **Input Validation**: Comprehensive parameter validation

Quick Start
-----------

.. code-block:: python

   from mymt5 import MT5Client, MT5Account, MT5Trade

   # Connect to MT5
   client = MT5Client()
   client.initialize(login=12345678, password='pass', server='server')

   # Get account info
   account = MT5Account(client)
   balance = account.get('balance')
   print(f"Balance: ${balance}")

   # Execute trade
   trade = MT5Trade(client)
   result = trade.buy(symbol='EURUSD', volume=0.01)

   # Cleanup
   client.shutdown()

Installation
------------

.. code-block:: bash

   pip install -e .

Or install from source:

.. code-block:: bash

   git clone https://github.com/yourusername/mymt5.git
   cd mymt5
   pip install -e .

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   quickstart
   user_guide
   installation
   configuration
   troubleshooting

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/client
   api/account
   api/symbol
   api/terminal
   api/data
   api/history
   api/trade
   api/risk
   api/validator
   api/utils
   api/enums

.. toctree::
   :maxdepth: 2
   :caption: Development

   contributing
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



