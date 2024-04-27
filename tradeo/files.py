"""Script to collect different files utilities."""
import typing as ty
from pathlib import Path
from os.path import exists
import json
import os
from time import sleep
from json.decoder import JSONDecodeError
from enum import Enum

from tradeo.paths import get_default_path

_default_path = get_default_path()


class Files(str, Enum):
  """Files enum."""

  # GENERAL
  SUCCESSFUL_SYMBOLS = 'successful_symbols.txt'
  CONSECUTIVE_TIMES_DOWN = 'consecutive_times_down.txt'
  LAST_BALANCE = 'last_balance.txt'


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


def try_read_file(file_path: Path) -> str:
  """Try to read a file."""
  try:
    with open(file_path, 'r') as f:
      return f.read()
  except IOError:
    pass
  return ''


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


def remove_file(
    file_name: str,
    file_path: Path = _default_path
) -> None:
  """Remove a file."""
  path = file_path if file_path != _default_path else get_default_path()
  os.remove(path / file_name)


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
