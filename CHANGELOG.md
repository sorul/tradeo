# CHANGELOG

## v0.23.1 (12/05/2025)
- fix:
  - Update setuptools dev dependecy to 80.8.0 version for fixing vulnerability issue.

## v0.23.0 (12/02/2025)
- refactor:
  - From now on, the minimum python version is 3.10.0
- fix:
  - calculate_heikin_ashi method preservs the volume from input data.

## v0.22.0 (26/01/2025)
- feat:
  - New methods in "trading_methods" script:
    - calculate_poc_vah_val
    - calculate_heikin_ashi
  - MT_client constructor has a new parameter "convert_to_utc".
- fix:
  - Now MT_Client uses a system to block threads so that the same symbol cannot enter the function "check_historical_data" multiple times.
  - Only new messages are included in MT_Client.messages object.
  - get_bid_ask improved to obtain bid and ask values.
  - The "place_break_even" and "_check_if_break_even_can_be_placed" methods are fixed.
- refactor:
  - Log improvements to work in multithreading.
  - Message constructor receives a datetime instead of a string for "time" parameter.
  - The OHLC class is improved to support different inputs formats.

## V0.21.0 (16/11/2024)
- refactor:
  - The mt_client parameter is now in the Strategy constructor.

## V0.20.0 (16/11/2024)
- fix:
  - Now there is an option to disable the loggings feature.

## V0.19.0 (09/11/2024)
- refactor:
  - python versions updated (>= 3.9.0, <4.0.0)
  - "_check_mt_needs_to_restart" function remove from BasicForex class.
  - compile file "mt_tb_expert.ex5" uploaded
  - New Blocker class to lock the executions
- feat:
  - "reboot_mt" function removed.
  - the folder to write agent files is a new input in the MT Advisor

## V0.18.0 (25/05/2024)
- feat:
  - MT_Client has a new method called "get_lot_size".
- fix:
  - "test_clean_messages" and "test_get_balance" fixed.

## V0.17.1 (15/05/2024)
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
