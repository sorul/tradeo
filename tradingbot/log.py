"""Script to handle logging."""

import logging
import socket
from logging.handlers import SysLogHandler
from .singleton import Singleton
from .config import Config


"""URL: https://my.papertrailapp.com/events ."""


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
    self.logger = logging.getLogger()
    self.logger.setLevel(Config.log_level)

    self.syslog = SysLogHandler(
        address=(Config.syslog_address, Config.syslog_port))

    self.syslog.addFilter(ContextFilter())
    self.formatter = logging.Formatter(
        '%(asctime)s %(levelname)s trading-bot: %(message)s',
        datefmt='%b %d %H:%M:%S')

    self.syslog.setFormatter(self.formatter)
    self.logger.addHandler(self.syslog)

  def debug(self, msg: str):
    """Log debug message."""
    self.logger.debug(msg)

  def info(self, msg: str):
    """Log info message."""
    self.logger.info(msg)

  def warning(self, msg: str):
    """Log warning message."""
    self.logger.warning(msg)

  def error(self, msg: str):
    """Log error message."""
    self.logger.error(msg.replace('\n', ' '))


# Singleton instance
log = Log()
