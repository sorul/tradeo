# FOREX TRADINGBOT - METATRADER

Still in development 🛠️


## Forex bot execution

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
".env.forex" file and then execute the command using Poetry:

```bash
source .env.forex
poetry run run_forex
```