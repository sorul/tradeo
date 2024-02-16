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

# Logging configuration
export TB_LOG_LEVEL=INFO

# Metatrader configuration
export TB_WINE_PATH=/usr/local/bin/wine
export TB_WINE_HOME="/home/${USER}/.wine"
export TB_MT_TERMINAL_EXE="${TB_WINE_HOME}/drive_c/Program Files/MetaTrader/terminal.exe"
export TB_MT_FILES_PATH="${TB_WINE_HOME}/drive_c/Program Files/MetaTrader/MQL5/Files"

```

The different possibilities for exporting environment variables depend on
the user's preference. For example, we can place all the variables in a
".env.forex" file and then execute the command using Poetry.:

```bash
source .env.forex
poetry run run_forex
```