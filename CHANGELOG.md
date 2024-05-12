# CHANGELOG

## V0.17.1 (develop)
- build:
  - python version modified in pyproject.toml
- fix:
  - agentfile folder fixed
  - there were tests that caused the execution not to finish

## V0.17.0 (05/05/2024)
- test:
  - "pytest-cov" dependency added. A 90 percent coverage exceeded.

## V0.16.1 (27/04/2024)
- docs:
  - Updating install section of README.md file.

## V0.16.0 (27/04/2024)
- refactor:
  - Change the package name from "tradingbot" to "tradeo".

## ** V0.15.0 (16/04/2024) **
- feat:
  - MT_MessageError and MT_MessageInfo for handle MetaTrader messages.
  - "get_error_messages" and "get_info_messages" new methods from MT_Client.
- docs:
  - README completed.
  - LICENSE added.

## ** V0.14.0  (08/04/2024) **
- refactor:
  - Successful symbols are now an attribute of MT_Client class instead of a file
- fix:
  - Bug about order type in order creation fixed

## ** V0.13.0  (08/04/2024) **
- feat:
  - New Blocker class to lock the executions
  - Order object has a new __str__() method
- refactor:
  - Several methods are moved from one module to another
- fix:
  - $USER environment variable updated to $HOME variable
  - We retrieve the environment variables from MetaTrader
  - Bug about remaining symbols fixed
  - Bug about command files fixed

## ** V0.12.1  (08/04/2024) **
- fix:
  - New structure of folders to solve files issues.

## ** V0.12.0  (31/03/2024) **
- feat:
  - New attribute PNL in Order object
  - New attribute **kwargs in Strategy static methods
- fix:
  - "TB_STRATEGIES" and "TB_EVENT_HANDLER_CLASS" variables removed 

## ** V0.11.1  (31/03/2024) **
- refactor:
  - The necessary changes are made to prepare for the first tag

## ** V0.11.0  (31/03/2024) **
- feat:
  - Factory classes removed

## ** V0.10.0  (30/03/2024) **
- feat:
  - Executable class for custom your own bots

## ** V0.9.0  (30/03/2024) **
- feat:
  - Telegram handle for logging

## ** V0.8.0  (13/03/2024) **
- feat:
  - New method "handle_trades" in forex.py


## ** V0.7.0  (12/03/2024) **
- feat:
  - New method "create_new_order" in mt_client.py
- test:
  - test_create_new_order method.


## ** V0.6.0  (18/02/2024) **
- feat:
  - EventHandler class to process every incoming trading response.
  - Strategy factory.


## ** V0.5.1  (12/02/2024) **
- fix:
  - "symbol" variable relocate in ImmutableOrderDetails class

## ** V0.5.0  (12/02/2024) **
- feat:
  - new ema strategy
- test:
  - ema strategy

## ** V0.4.0  (11/02/2024) **
- feat:
  - strategy abstract class
  - common useful methods in trading
  - new methods in forex_client: get_bid_ask, place_break_even and get_pip
- test:
  - strategy abstract class
  - common useful methods in trading

## ** V0.3.0  (25/01/2024) **
- feat:
  - forex main to handle incoming historical data
  - support methods
- test
  - forex main

## ** V0.2.0  (18/01/2024) **
- feat:
  - agent in MQL5
  - files utils
  - new util method
  - new config parameters
- test
  - files utils
  - agent in MQL
  - utils
  - forex client

## ** V0.1.0  (05/01/2024) **
- feat:
  - forex handle
  - paths utils
- test
  - forex handle
  - paths
- ci
  - Makefile construction
