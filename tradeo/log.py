"""Script to handle logging."""

import logging
import socket
from logging.handlers import SysLogHandler
from logging import Handler
import requests
import threading

from tradeo.singleton import Singleton
from tradeo.config import Config


"""URL: https://my.papertrailapp.com/events ."""


class TelegramHandler(Handler):
  """Handler to send logs to telegram."""

  def emit(self, record):
    """Send the log to telegram."""
    log_entry = self.format(record)
    payload = {
        'chat_id': Config.forex_telegram_chat_id,
        'text': log_entry,
        'parse_mode': 'HTML'
    }
    token = Config.forex_telegram_token
    return requests.post(
        f'https://api.telegram.org/bot{token}/sendMessage',
        data=payload
    ).content


class ContextFilter(logging.Filter):
  """Filter to add hostname to log record."""

  hostname = socket.gethostname()

  def filter(self, record):  # noqa
    """Add the hostname 'e.g. raspberrypi' to the log record."""
    record.hostname = ContextFilter.hostname
    return True  # No filtering


class Log(metaclass=Singleton):
  """Class to manage logging."""

  def __init__(self):
    """Initialize the logger."""
    self.logger = logging.getLogger('tradeo')
    self.logger.setLevel(logging.DEBUG)

    # Thread-local storage for handlers
    self.thread_local = threading.local()

  def _initialize_thread_handlers(self):
    """Initialize unique handlers for each thread."""
    if not hasattr(self.thread_local, 'handlers_initialized'):
      self.thread_local.handlers_initialized = True

      if Config.activate_syslog:
        self._build_log()
      if Config.activate_telegram:
        self._build_telegram_log()

  def _build_log(self) -> None:
    handler = SysLogHandler(
        address=(Config.syslog_address, Config.syslog_port))

    # Filter
    handler.addFilter(ContextFilter())
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s trading-bot: %(message)s',
        datefmt='%b %d %H:%M:%S')

    # Format
    handler.setFormatter(formatter)

    # Level
    handler.setLevel(Config.log_level)

    # Add the handler
    self.logger.addHandler(handler)

  def _build_telegram_log(self) -> None:
    handler = TelegramHandler()

    # Level
    handler.setLevel(Config.tg_log_level)

    # Add the handler
    self.logger.addHandler(handler)

  def debug(self, msg: str):
    """Log debug message."""
    self._initialize_thread_handlers()
    self.logger.debug(msg)

  def info(self, msg: str):
    """Log info message."""
    self._initialize_thread_handlers()
    self.logger.info(msg)

  def warning(self, msg: str):
    """Log warning message."""
    self._initialize_thread_handlers()
    self.logger.warning(f'🟡 {msg}')

  def error(self, msg: str):
    """Log error message."""
    self._initialize_thread_handlers()
    msg = msg.replace('\n', ' ')
    self.logger.error(f'🔴 {msg}')


# Singleton instance
log = Log()
