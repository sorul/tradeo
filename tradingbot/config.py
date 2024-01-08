"""Script to manage envs files."""
from dotenv import load_dotenv
from .paths import config_path
import logging
import os
import pytz


class Config:
  """Class to manage config."""

  load_dotenv(dotenv_path=config_path() / 'env' / '.env.demo')

  # Timezone Configuration
  local_timezone = pytz.timezone(
      os.getenv('LOCAL_TIMEZONE') or 'Europe/Madrid')
  forex_timezone = pytz.timezone(
      os.getenv('FOREX_TIMEZONE') or 'US/Eastern')
  broker_timezone = pytz.timezone(
      os.getenv('BROKER_TIMEZONE') or '')

  # Paths configuration
  zmq_files_path = os.getenv('ZMQ_FILES_PATH')

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
