"""Script to manage envs files."""
from pathlib import Path
import logging
import os
import pytz
from typing import Union


def _get_bool_from_env(env_name: str) -> Union[bool, None]:
  """Get bool from env."""
  e = os.getenv(env_name)
  if e is None:
    return None
  else:
    return str(e).lower() in ['true', '1']


def _get_logging_level(level: str) -> int:
  if level.lower() in ['info', 'inf', 'information']:
    log_level = logging.INFO
  elif level.lower() in ['debug', 'deb', 'debugging']:
    log_level = logging.DEBUG
  elif level.lower() in ['warning', 'warn']:
    log_level = logging.WARNING
  elif level.lower() in ['error', 'err']:
    log_level = logging.ERROR
  else:
    raise ValueError(f'Invalid log level: {level}')
  return log_level


class Config:
  """Class to manage config."""

  # Timezone Configuration
  local_timezone = pytz.timezone(
      os.getenv('TB_LOCAL_TIMEZONE') or 'Europe/Madrid')
  broker_timezone = pytz.timezone(
      os.getenv('TB_BROKER_TIMEZONE') or 'Etc/GMT-2')
  utc_timezone = pytz.utc

  # Paths configuration
  home = os.environ['HOME']
  default_mt_files_path = Path(
      f'{home}/.wine/drive_c/Program Files/MetaTrader/MQL5/Files'
  )
  mt_files_path = Path(os.getenv('TB_MT_FILES_PATH') or default_mt_files_path)

  # Trading configuration
  symbols = (os.getenv('TB_SYMBOLS') or 'EURUSD,USDJPY,USDCAD').split(',')
  timeframe = os.getenv('TB_TIMEFRAME') or 'M5'
  lookback_days = int(os.getenv('TB_LOOKBACK_DAYS') or 10)

  # Forex client configuration
  check_messages_thread = _get_bool_from_env(
      'TB_CHECK_MESSAGES_THREAD') or True
  check_market_data_thread = _get_bool_from_env(
      'TB_CHECK_MARKET_DATA_THREAD') or True
  check_bar_data_thread = _get_bool_from_env(
      'TB_CHECK_BAR_DATA_THREAD') or True
  check_open_orders_thread = _get_bool_from_env(
      'TB_CHECK_OPEN_ORDERS_THREAD') or True
  check_historical_data_thread = _get_bool_from_env(
      'TB_CHECK_HISTORICAL_DATA_THREAD') or True
  check_historical_trades_thread = _get_bool_from_env(
      'TB_CHECK_HISTORICAL_TRADES_THREAD') or True

  # Logging configuration
  syslog_address = os.getenv('TB_SYSLOG_ADDRESS') or 'logs2.papertrailapp.com'
  syslog_port = int(os.getenv('TB_SYSLOG_PORT') or 43931)
  log_level = _get_logging_level(os.getenv('TB_LOG_LEVEL') or 'DEBUG')

  # Telegram configuration
  forex_telegram_token = os.getenv(
      'TB_TG_FOREX_TOKEN') or ''
  forex_telegram_chat_id = int(os.getenv('TB_TG_FOREX_CHAT_ID') or 0)
  tg_log_level = _get_logging_level(os.getenv('TB_TG_LOG_LEVEL') or 'DEBUG')
