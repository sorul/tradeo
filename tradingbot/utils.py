"""Script to collect different utilities."""
from time import sleep
from datetime import datetime
from .config import Config
from .paths import data_path, bash_path
from .files import lock, unlock, Files
from .files import Files as f
import subprocess
import typing as ty
from .log import log
from os.path import basename, join
from pytz import BaseTzInfo
from pytz.tzinfo import DstTzInfo, StaticTzInfo

timezone_type = ty.Union[DstTzInfo, BaseTzInfo, StaticTzInfo]


def string_to_date_utc(
    str_date: str,
    date_format: str = '%Y.%m.%d %H:%M',
    timezone: timezone_type = Config.utc_timezone
) -> datetime:
  """Convert a string to a datetime object in UTC timezone."""
  r = timezone.localize(datetime.strptime(str_date, date_format))
  return r.astimezone(Config.utc_timezone)


def get_script_name() -> str:
  """Return the name of the script."""
  return basename(__file__).replace('.py', '')


def add_successful_symbol(symbol: str) -> None:
  """Add a symbol to the successful symbols file."""
  path = data_path().joinpath(Files.SUCCESSFUL_SYMBOLS.value)
  with open(path, 'a') as file:
    file.write(f'{symbol}\n')


def get_successful_symbols() -> ty.List[str]:
  """Return the list of successful symbols."""
  path = data_path().joinpath(Files.SUCCESSFUL_SYMBOLS.value)
  with open(path, 'r') as file:
    lines = file.readlines()
    symbols = [symbol.strip() for symbol in lines]
  return symbols


def get_remaining_symbols() -> ty.List[str]:
  """Return the list of remaining symbols."""
  all_symbols = set(Config.symbols)
  successful_symbols = set(get_successful_symbols())
  return list(all_symbols - successful_symbols)


def reboot_mt():
  """Reboot MetaTrader."""
  log.warning('Rebooting MetaTrader ...')
  lock(f.FOREX_LOCK)
  scripts_path = bash_path()
  subprocess.Popen(['/usr/bin/sh', join(scripts_path, 'stop-mt.sh')])
  sleep(3)
  subprocess.Popen(['/usr/bin/sh', join(scripts_path, 'launch-mt5.sh')])
  sleep(60)
  unlock(f.FOREX_LOCK)


def create_magic_number() -> str:
  """Create a magic number based on the current date and time."""
  return str(
      round(datetime.now(Config.utc_timezone).timestamp())
  ).replace('.', '')
