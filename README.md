# TRADEO - A forex trading framework using MetaTrader
![Logo](docs/images/logo.PNG "Title")

This library contains a series of tools to create a trading bot for Forex trading. It uses the [DWX Connect](https://github.com/darwinex/dwxconnect/) (modified) to send commands and receive information of MetaTrader.
This library is created **based on a linux installation of MetaTrader**.

![Test](https://github.com/sorul/tradeo/actions/workflows/testing_coverage.yml/badge.svg?branch=master)
![codecov.io](https://codecov.io/github/sorul/tradeo/coverage.svg?branch=master)

## Installation

### Install the library

#### PIP
```shell
pip install tradeo
```

#### POETRY
```shell
poetry add tradeo
```

Or you can add manually in *pyproject.toml* file if you want download it from a specific branch:

```shell
tradeo = { git = "git@github.com:sorul/tradeo.git", branch = "develop" }
```

## Usage

- You can create strategies inheriting *tradeo.strategies.strategy.Strategy* class. An example of this it would be [basic_strategy.py](tradeo/strategies/basic_strategy.py)

- You can customize the handler of metatrader responses inheriting *tradeo.event_handlers.event_handler.EventHandler* class. An example of this it would be [basic_handler.py](tradeo/event_handlers/basic_event_handler.py)

- An example of a main script using this library would be [basic_forex.py](tradeo/executable/basic_forex.py) that inheriting *tradeo.executable.executable.Executable*.

> [!NOTE]  
> **The configuration of Metatrader is necessary for the functioning of Tradeo.** There is an example of both the configuration and the use of the library in a real project: [sorul_tradingbot](https://github.com/sorul/sorul_tradingbot)

## Utilities
- *tradeo.utils.logger* module: It contains a logger that can be used in your project. It can be configured to log in a file, in the console or in a syslog server. It also has the possibility of sending logs to a Telegram chat.
- *tradeo.trading_methods* module: It contains some trading methods that can be used in your strategies, such as calculating the pivots, calculating POH, VAL, VAH, calculating the EMA, RSI, etc.

### Forex client background threads

The `MT_Client.start()` method starts background threads that poll files
written by the MetaTrader expert advisor. Some files are written
continuously by the expert advisor, while others are only generated after the
Python client sends a command or subscription request.

| Thread | Method called by the thread | Requires a previous command? | Reason |
|---|---|---:|---|
| `start_thread_check_messages` | `check_messages()` | No | The expert advisor writes `Messages.json` when it emits info/error messages. |
| `start_thread_check_market_data` | `check_market_data()` | Yes | Requires `subscribe_symbols(...)`, which sends `SUBSCRIBE_SYMBOLS`. Otherwise, the expert advisor has no symbols in `MarketDataSymbols`. |
| `start_thread_check_bar_data` | `check_bar_data()` | Yes | Requires `subscribe_symbols_bar_data(...)`, which sends `SUBSCRIBE_SYMBOLS_BAR_DATA`. Otherwise, `BarDataInstruments` is empty. |
| `start_thread_check_open_orders` | `check_open_orders()` | No | The expert advisor runs `CheckOpenOrders()` on every tick/timer cycle and writes `Orders.json` continuously. |
| `start_thread_check_historical_data` | `check_historical_data()` | Yes | Requires `get_historical_data(symbol, timeframe)`, which sends `GET_HISTORICAL_DATA`. Otherwise, no fresh `Historical_Data_<symbol>.json` file is generated. |
| `start_thread_check_and_update_historical_trades` | `get_historical_trades()` and `check_historical_trades()` | No | The thread periodically sends `GET_HISTORICAL_TRADES` and then reads the generated `Historical_Trades.json` file. The refresh interval is configured through the `MT_Client` constructor. |

In short:

```text
No previous command required:
- start_thread_check_messages
- start_thread_check_open_orders

Previous subscription required:
- start_thread_check_market_data
- start_thread_check_bar_data

Previous explicit request required:
- start_thread_check_historical_data

Automatically requested by its own thread:
- start_thread_check_and_update_historical_trades
```

For critical workflows where stale closed-trade history could cause a wrong
decision, such as opening a duplicate order after a position has just closed,
use:

```python
mt_client.ensure_historical_trades_current(
    timeout_seconds=5,
    max_age_seconds=120,
    lookback_days=2,
)
```

This helper loads a recent `Historical_Trades.json` snapshot and, when the file
is missing or stale, sends `GET_HISTORICAL_TRADES` once before waiting for a
fresh file.

## Execution of your project if you import this library

It's necessary to export certain environment variables before running the bot.
The `TB_CHECK_*_THREAD` variables in the Forex-Client configuration decide
which `MT_Client` background threads are enabled or disabled when
`MT_Client.start()` is called. See the "Forex client background threads" section
above for what each thread consumes and whether it needs a previous command or
subscription.

```bash
# Timezone configuration
export TB_LOCAL_TIMEZONE=Europe/Madrid
export TB_BROKER_TIMEZONE=Etc/GMT-2

# Trading configuration
export TB_SYMBOLS=EURUSD,USDCAD,USDCHF
export TB_ACCOUNT_CURRENCY=EUR
export TB_TIMEFRAME=M5
export TB_LOOKBACK_DAYS=10

# Forex-Client configuration
export TB_CHECK_MESSAGES_THREAD=true
export TB_CHECK_MARKET_DATA_THREAD=false
export TB_CHECK_BAR_DATA_THREAD=false
export TB_CHECK_OPEN_ORDERS_THREAD=true
export TB_CHECK_HISTORICAL_DATA_THREAD=true
export TB_CHECK_HISTORICAL_TRADES_THREAD=false

# Metatrader configuration
export TB_WINE_HOME="${HOME}/.wine"
export TB_MT_FILES_PATH="${TB_WINE_HOME}/drive_c/.../MQL5/Files"

# Logging configuration
export TB_ACTIVATE_SYSLOG=false
export TB_LOG_LEVEL=INFO
export TB_SYSLOG_ADDRESS=logs2.papertrailapp.com
export TB_SYSLOG_PORT=12345

# Telegram configuration
export TB_ACTIVATE_TELEGRAM=false
export TB_TG_LOG_LEVEL=INFO
export TB_TG_FOREX_TOKEN=0000000000:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
export TB_TG_FOREX_CHAT_ID=-999999999
```

The different possibilities for exporting environment variables depend on
the user's preference. For example, we can place all the variables in a
".env" file and then execute the command using a Makefile and poetry:

*Makefile*
```makefile
run_forex:
	source .env && ~/.local/bin/poetry run run_forex
```

Edit the crontab (crontab -e):

```console
@reboot cd <path_to_your_project> && make start_metatrader

*/5 * * * 0-5  cd <path_to_your_project> && make run_forex
```
