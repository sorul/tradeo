"""Script to manage envs files."""
from dotenv import load_dotenv
from .paths import config_path
from pathlib import Path
import logging
import os
import pytz


class Config:
  """Class to manage config."""

  load_dotenv(dotenv_path=config_path() / 'env' / '.env.demo')

  # Timezone Configuration
  local_timezone = pytz.timezone(
      os.getenv('LOCAL_TIMEZONE') or 'Europe/Madrid')
  broker_timezone = pytz.timezone(
      os.getenv('BROKER_TIMEZONE') or '')
  utc_timezone = pytz.utc

  # Paths configuration
  default_mt_files_path = Path(
      '/home/pi/.wine/drive_c/Program Files/MetaTrader/MQL5/Files')
  mt_files_path = Path(os.getenv('MT_FILES_PATH') or default_mt_files_path)

  # Trading configuration
  symbols = (os.getenv('SYMBOLS') or 'EURUSD').split(',')
  timeframe = os.getenv('TIMEFRAME') or 'M5'
  lookback_days = float(os.getenv('LOOKBACK_DAYS') or 10)

  # Logging configuration
  ll = os.getenv('LOG_LEVEL') or 'INFO'
  if ll == 'INFO':
    log_level = logging.INFO
  elif ll == 'DEBUG':
    log_level = logging.DEBUG
  elif ll == 'WARNING':
    log_level = logging.WARNING
  elif ll == 'ERROR':
    log_level = logging.ERROR
  else:
    log_level = ll
