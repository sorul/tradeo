"""Script to collect different utilities."""
from time import sleep
from datetime import datetime
import subprocess
import typing as ty
from os.path import join
from pytz import BaseTzInfo
from pytz.tzinfo import DstTzInfo, StaticTzInfo

from tradeo.config import Config
from tradeo.paths import bash_path, get_default_path
from tradeo.files import Files
from tradeo.files import write_file, try_read_file
from tradeo.log import log

timezone_type = ty.Union[DstTzInfo, BaseTzInfo, StaticTzInfo]


def string_to_date_utc(
    str_date: str,
    date_format: str = '%Y.%m.%d %H:%M',
    from_timezone: timezone_type = Config.utc_timezone
) -> datetime:
  """Convert a string to a datetime object in UTC timezone."""
  r = from_timezone.localize(datetime.strptime(str_date, date_format))
  return r.astimezone(Config.utc_timezone)


def reboot_mt():
  """Reboot MetaTrader."""
  log.warning('Rebooting MetaTrader ...')
  scripts_path = bash_path()
  subprocess.Popen(['/usr/bin/sh', join(scripts_path, 'stop-mt.sh')])
  sleep(3)
  subprocess.Popen(['/usr/bin/sh', join(scripts_path, 'launch-mt5.sh')])
  sleep(60)


def create_magic_number() -> str:
  """Create a magic number based on the current date and time."""
  return str(
      round(datetime.now(Config.utc_timezone).timestamp())
  ).replace('.', '')


def reset_consecutive_times_down() -> None:
  """Reset the consecutive times down file."""
  write_file(Files.CONSECUTIVE_TIMES_DOWN.value, '0')


def get_last_balance() -> float:
  """Get the balance of the account."""
  path = get_default_path()
  return float(try_read_file(path / Files.LAST_BALANCE.value))


def get_consecutive_times_down() -> int:
  """Get the consecutive times down."""
  path = get_default_path()
  return int(try_read_file(path / Files.CONSECUTIVE_TIMES_DOWN.value))


def increment_consecutive_times_down() -> None:
  """Increment the consecutive times down."""
  write_file(Files.CONSECUTIVE_TIMES_DOWN.value,
             str(get_consecutive_times_down() + 1))
