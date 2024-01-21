"""Script to collect different files utilities."""
import typing as ty
from pathlib import Path
from tradingbot.paths import config_path, data_path
from os.path import exists
import json
import os
from time import sleep
from json.decoder import JSONDecodeError


def get_successful_symbols() -> ty.List[str]:
  """Return the list of successful symbols."""
  path = data_path().joinpath('successful_symbols.txt')
  with open(path, 'r') as file:
    lines = file.readlines()
    symbols = [symbol.strip() for symbol in lines]
  return symbols


def file_exists(file: str, path: Path = config_path()) -> bool:
  """Return True if the file exists."""
  return exists(path / file)


def try_load_json(file_path: Path) -> ty.Dict[str, ty.Dict]:
  """Try to load a JSON from a file generate from MQL."""
  try:
    if exists(file_path):
      with open(file_path) as f:
        text = f.read()
        return json.loads(text)
  except (IOError, PermissionError, JSONDecodeError):
    pass
  return {}


def try_read_file(file_path: Path) -> str:
  """Try to read a file."""
  for _ in range(5):
    if file_path.exists():
      try:
        with open(file_path, 'r') as f:
          return f.read()
      except (IOError, PermissionError, FileNotFoundError):
        pass
      sleep(0.1)
  return ''


def try_remove_file(file_path: Path) -> bool:
  """Try to remove a file."""
  for _ in range(5):
    if file_path.exists():
      try:
        os.remove(file_path)
        return True
      except (IOError, PermissionError, FileNotFoundError):
        pass
      sleep(0.1)
  return False
