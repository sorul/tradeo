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

  def filter(self, record):
    """Add the hostname 'e.g. raspberrypi' to the log record."""
    record.hostname = ContextFilter.hostname
    return True  # No filtering


class Log(metaclass=Singleton):
  """Class to manage logging."""

  def __init__(self):
    """Initialize the logger."""
    self.logger = logging.getLogger()
    self.logger.setLevel(Config.log_level)

    self.syslog = SysLogHandler(address=('logs2.papertrailapp.com', 43931))

    self.syslog.addFilter(ContextFilter())
    self.formatter = logging.Formatter(
        '%(asctime)s %(levelname)s trading-bot: %(message)s',
        datefmt='%b %d %H:%M:%S')

    self.syslog.setFormatter(self.formatter)
    self.logger.addHandler(self.syslog)

  def debug(self, msg):
    """Log debug message."""
    self.logger.debug(msg)

  def info(self, msg):
    """Log info message."""
    self.logger.info(msg)

  def warning(self, msg):
    """Log warning message."""
    self.logger.warning(msg)

  def error(self, msg):
    """Log error message."""
    self.logger.error(msg)


# Singleton instance
log = Log()
