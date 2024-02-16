"""Script to manage envs files."""
from pathlib import Path
import logging
import os
import pytz


class Config:
  """Class to manage config."""

  # Timezone Configuration
  local_timezone = pytz.timezone(
      os.getenv('TB_LOCAL_TIMEZONE') or 'Europe/Madrid')
  broker_timezone = pytz.timezone(
      os.getenv('TB_BROKER_TIMEZONE') or 'Etc/GMT-2')
  utc_timezone = pytz.utc

  # Paths configuration
  user = os.environ['USER']
  default_mt_files_path = Path(
      f'/home/{user}/.wine/drive_c/Program Files/MetaTrader/MQL5/Files'
  )
  mt_files_path = Path(os.getenv('TB_MT_FILES_PATH') or default_mt_files_path)

  # Trading configuration
  symbols = (os.getenv('TB_SYMBOLS') or 'EURUSD,USDJPY,USDCAD').split(',')
  timeframe = os.getenv('TB_TIMEFRAME') or 'M5'
  lookback_days = float(os.getenv('TB_LOOKBACK_DAYS') or 10)

  # Logging configuration
  syslog_address = os.getenv('TB_SYSLOG_ADDRESS') or 'logs2.papertrailapp.com'
  syslog_port = int(os.getenv('TB_SYSLOG_PORT') or 43931)
  ll = os.getenv('TB_LOG_LEVEL') or 'INFO'
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
