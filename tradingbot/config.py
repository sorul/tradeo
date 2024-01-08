"""Script to manage envs files."""
from dotenv import load_dotenv
from .paths import config_path
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
