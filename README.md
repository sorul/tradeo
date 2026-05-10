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

Tradeo is built around three small pieces:

- A strategy decides whether a candle snapshot should become an order. See [basic_strategy.py](tradeo/strategies/basic_strategy.py).
- An event handler receives MetaTrader responses and calls your strategy. See [basic_event_handler.py](tradeo/event_handlers/basic_event_handler.py).
- An executable wires everything together: starts the client, asks MetaTrader for data, handles open trades and waits for new candles. See [basic_forex.py](tradeo/executable/basic_forex.py).

The main object is `MT_Client`. It talks to MetaTrader through files written in
the `MQL5/Files/AgentFiles` folder. You can let it poll those files in
background threads, or you can request data and wait for it explicitly.

> [!NOTE]  
> **The configuration of Metatrader is necessary for the functioning of Tradeo.** There is an example of both the configuration and the use of the library in a real project: [sorul_tradingbot](https://github.com/sorul/sorul_tradingbot)

## Utilities
- *tradeo.utils.logger* module: It contains a logger that can be used in your project. It can be configured to log in a file, in the console or in a syslog server. It also has the possibility of sending logs to a Telegram chat.
- *tradeo.trading_methods* module: It contains some trading methods that can be used in your strategies, such as calculating the pivots, calculating POH, VAL, VAH, calculating the EMA, RSI, etc.

### MT_Client pollers

`MT_Client.start()` can launch small background pollers. Each poller watches one
MetaTrader file and updates the in-memory client state.

For interval-based bots, the clearest setup is usually:

```python
mt_client = MT_Client(
    event_handler=BasicEventHandler(),
    pollers={
        'messages': True,
        'market_data': True,
        'bar_data': False,
        'open_orders': True,
        'historical_data': False,
        'historical_trades': False,
    },
)
```

That means:

| Poller | Reads | Most useful for |
|---|---|---|
| `messages` | `Messages.json` | Almost every live bot. It keeps MetaTrader errors and info messages available so the bot can report failed commands, wrong order formats or broker-side rejections. |
| `market_data` | `Market_Data.json` | Bots that need current bid/ask while managing orders: break-even logic, trailing stops, pending-order type detection, spread checks, or lot/risk calculations. Enable it after `subscribe_symbols(...)`. |
| `bar_data` | `Bar_Data.json` | Always-on bots that want live candle updates from `subscribe_symbols_bar_data(...)`, for example a dashboard or a process that reacts as soon as a new M1/M5 bar is published. Leave it off for cron-style bots that request candles explicitly. |
| `open_orders` | `Orders.json` | Bots that manage existing positions or account state: closing unknown orders, moving stop loss, reading balance/equity, avoiding duplicate open orders, or reporting current exposure. |
| `historical_data` | `Historical_Data_<symbol>.json` | Long-running, event-driven bots that send `get_historical_data(...)` requests and want `on_historical_data(...)` to fire in the background. For interval-based bots, `request_historical_data(...)` plus `wait_historical_data(...)` is usually clearer. |
| `historical_trades` | `Historical_Trades.json` | Always-on bots that need closed trades refreshed periodically, for example daily PnL tracking or duplicate-trade prevention across the whole session. For interval-based bots, `ensure_historical_trades_current(...)` before making decisions is usually enough. |

If `pollers` is not provided, Tradeo reads the `TB_CHECK_*_THREAD` environment
variables instead. This is useful when you prefer to configure the runtime from
a `.env` file rather than making the Python call explicit.

### Request data explicitly

For a bot that runs every few minutes, prefer this flow:

```python
mt_client.start()
mt_client.request_historical_data(Config.symbols, Config.timeframe)
mt_client.subscribe_symbols(Config.symbols)

# handle existing trades first
orders = mt_client.check_open_orders()

# then process the candles requested above
remaining_symbols = mt_client.wait_historical_data(
    Config.symbols,
    timeout_seconds=240,
)
```

`wait_historical_data(...)` calls `check_historical_data(...)` internally, so
your `event_handler.on_historical_data(...)` still receives the candle snapshot.
The example executable [basic_forex.py](tradeo/executable/basic_forex.py) uses
this style.

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

This is intentionally different from enabling the `historical_trades` poller:

- Use `historical_trades=True` when your application is always running and you
  want closed trades to refresh periodically in the background.
- Use `historical_trades=False` plus `ensure_historical_trades_current(...)`
  when your bot runs by intervals and only needs a fresh snapshot before making
  a decision.

Using both is usually redundant for interval-based bots. It can make sense for
an always-on application that wants background refreshes most of the time, but
still needs to force a freshness check before a critical decision.

## Execution of your project if you import this library

You usually need environment variables for timezones, symbols, MetaTrader paths
and logging. Pollers can also be configured from the environment when you do not
want to pass `pollers={...}` in Python.

```bash
# Timezone configuration
export TB_LOCAL_TIMEZONE=Europe/Madrid
export TB_BROKER_TIMEZONE=Etc/GMT-2

# Trading configuration
export TB_SYMBOLS=EURUSD,USDCAD,USDCHF
export TB_ACCOUNT_CURRENCY=EUR
export TB_TIMEFRAME=M5
export TB_LOOKBACK_DAYS=10

# Optional Forex-Client poller configuration
export TB_CHECK_MESSAGES_THREAD=true
export TB_CHECK_MARKET_DATA_THREAD=true
export TB_CHECK_BAR_DATA_THREAD=false
export TB_CHECK_OPEN_ORDERS_THREAD=true
export TB_CHECK_HISTORICAL_DATA_THREAD=false
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
