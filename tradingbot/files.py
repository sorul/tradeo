"""Script to collect different files utilities."""
import typing as ty
from pathlib import Path
from tradingbot.paths import get_default_path
from os.path import exists
import json
import os
from time import sleep
from json.decoder import JSONDecodeError
from enum import Enum

_default_path = get_default_path()


class Files(str, Enum):
  """Files enum."""

  # GENERAL
  SUCCESSFUL_SYMBOLS = 'successful_symbols.txt'
  CONSECUTIVE_TIMES_DOWN = 'consecutive_times_down.txt'
  LAST_BALANCE = 'last_balance.txt'

  # LOCKS
  FOREX_LOCK = 'forex.lock'
  NEW_ORDER_LOCK = 'new_order.lock'


def file_exists(file: str, file_path: Path = _default_path) -> bool:
  """Return True if the file exists.

  file_path: "get_default_path()" as default value.
  """
  path = file_path if file_path != _default_path else get_default_path()
  return exists(path / file)


def try_load_json(file_path: Path) -> ty.Dict[str, ty.Dict]:
  """Try to load a JSON from a file generate from MQL."""
  for _ in range(5):
    try:
      if exists(file_path):
        with open(file_path, 'r') as f:
          text = f.read()
          return json.loads(text)
    except (IOError, JSONDecodeError):
      pass
    sleep(0.1)
  return {}


def try_read_file(file_name: str, file_path: Path = _default_path) -> str:
  """Try to read a file."""
  path = file_path if file_path != _default_path else get_default_path()
  try:
    with open(path / file_name, 'r') as f:
      return f.read()
  except IOError:
    pass
  return ''


def lock(lock_name: str) -> None:
  """Create a lock file."""
  write_file(f'{lock_name}')


def unlock(lock_name: str) -> None:
  """Remove a lock file."""
  file_path = get_default_path()
  try_remove_file(file_path / f'{lock_name}')


def reset_successful_symbols_file() -> None:
  """Reset the successful symbols file."""
  write_file(Files.SUCCESSFUL_SYMBOLS.value, '')


def reset_consecutive_times_down_file() -> None:
  """Reset the consecutive times down file."""
  write_file(Files.CONSECUTIVE_TIMES_DOWN.value, '0')


def get_last_balance() -> float:
  """Get the balance of the account."""
  return float(try_read_file(Files.LAST_BALANCE.value))


def get_consecutive_times_down() -> int:
  """Get the consecutive times down."""
  return int(try_read_file(Files.CONSECUTIVE_TIMES_DOWN.value))


def increment_consecutive_times_down() -> None:
  """Increment the consecutive times down."""
  write_file(Files.CONSECUTIVE_TIMES_DOWN.value,
             str(get_consecutive_times_down() + 1))


def write_file(
    file_name: str,
    text: str = '',
    mode: str = 'w',
    file_path: Path = _default_path
) -> None:
  """Write a file.

  file_path: "get_default_path()" as default value.
  """
  path = file_path if file_path != _default_path else get_default_path()

  with open(file=path / file_name, mode=mode) as f:
    f.write(str(text))


def try_remove_file(file_path: Path) -> bool:
  """Try to remove a file."""
  for _ in range(5):
    if file_path.exists():
      try:
        os.remove(file_path)
        return True
      except IOError:
        pass
      sleep(0.1)
  return False
