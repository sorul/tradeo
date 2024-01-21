"""Script to collect different path utilities."""
from pathlib import Path


def root_project() -> Path:
  """Return the root project path."""""
  return Path(__file__).parent.parent


def config_path() -> Path:
  """Return the config path."""""
  return root_project() / 'config'


def data_path() -> Path:
  """Return the data path."""""
  return root_project() / 'data'
