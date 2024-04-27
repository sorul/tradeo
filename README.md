# TRADEO - A forex trading framework using MetaTrader

![alt text](docs/images/logo.PNG "Title")

This library contains a series of tools to create a trading bot for Forex trading. It uses the [DWX Connect](https://github.com/darwinex/dwxconnect/) (modified) to send commands and receive information of MetaTrader.
This library is created **based on a linux installation of MetaTrader**.

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
tradeo = { git = "git@github.com:sorul/tradeo.git", branch = "master" }
```

And finally:
```shell
poetry install --without dev
```



### Configure Metatrader

It is necessary to download the [mt_tb_expert.mq5](tradeo/mt_tb_expert.mq5) file and put it in the proper directory. This directory is usually: *MetaTrader/MQL5/Experts/Advisors/mt_tb_expert.mq5*.

We add the currency pairs in the timeframe we are going to use (in my case it would be 5 minutes). There is the option for the bot to open them automatically, but I do not recommend it.

Activate the expert in any symbol chart, it does not matter which chart you use. But only in one of them.

> [!TIP]
> If you want to execute MetaTrader in the background, your can use this [execute_mt5.sh](https://github.com/sorul/sorul_tradingbot/blob/master/scripts/execute_mt5.sh) script.


## Usage

- You can create strategies inheriting *tradeo.strategies.strategy.Strategy* class. An example of this it would be [basic_strategy.py](tradeo/strategies/basic_strategy.py)

- You can customize the handler of metatrader responses inheriting *tradeo.event_handlers.event_handler.EventHandler* class. An example of this it would be [basic_handler.py](tradeo/event_handlers/basic_event_handler.py)

- An example of a main script using this library would be [basic_forex.py](tradeo/tradeo/executable/basic_forex.py) that inheriting *tradeo.executable.executable.Executable*.

> [!NOTE]  
> A real project that imports this wonderful library and you can watch for inspiration is [sorul_tradingbot](https://github.com/sorul/sorul_tradingbot)



## Execution of your project if you import this library

It's necessary to export certain environment variables before running the bot.

```bash
# Timezone configuration
export TB_LOCAL_TIMEZONE=Europe/Madrid
export TB_BROKER_TIMEZONE=Etc/GMT-2

# Trading configuration
export TB_SYMBOLS=EURUSD,USDCAD,USDCHF
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
export TB_WINE_PATH=/usr/local/bin/wine
export TB_WINE_HOME="${HOME}/.wine"
export TB_MT_TERMINAL_EXE="${TB_WINE_HOME}/drive_c/Program Files/MetaTrader/terminal.exe"
export TB_MT_FILES_PATH="${TB_WINE_HOME}/drive_c/Program Files/MetaTrader/MQL5/Files"

# Logging configuration
export TB_LOG_LEVEL=INFO
export TB_SYSLOG_ADDRESS=logs2.papertrailapp.com
export TB_SYSLOG_PORT=43931

# Telegram configuration
export TB_TG_LOG_LEVEL=INFO
export TB_TG_FOREX_TOKEN=0000000000:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
export TB_TG_FOREX_CHAT_ID=-999999999
```

The different possibilities for exporting environment variables depend on
the user's preference. For example, we can place all the variables in a
".env" file and then execute the command using Poetry:

*main_forex.sh*
```bash
#!/bin/bash
PATH=/home/pi/.poetry/bin:/home/pi/.pyenv/shims:/home/pi/.pyenv/bin:/home/pi/.poetry/bin:/home/pi/.pyenv/shims:/home/pi/.pyenv/bin:/home/pi/.cargo/bin:/home/pi/.poetry/bin:/home/pi/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/games:/usr/games
SHELL=/usr/bin/bash
DISPLAY=:10.0
XAUTHORITY=/home/pi/.Xauthority
touch ~/.bashrc
cd <path_to_project>
source .env
poetry run run_forex
```

Edit the crontab (crontab -e):

```console
@reboot /usr/bin/env bash <path_to_your_project>/execute_mt5.sh

*/5 * * * 0-5 <path_to_your_project>/main_forex.sh >> /tmp/crontab_script_log.txt 2>&1
```