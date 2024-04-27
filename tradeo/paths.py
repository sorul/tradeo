"""Script to collect different path utilities."""
from pathlib import Path


def config_path() -> Path:
  """Return the config path."""
  return root_project() / 'config'


def bash_path() -> Path:
  """Return the bash path."""
  return bin_project() / 'bash'


def resources_test_path() -> Path:
  """Return the test resources path."""
  return root_project() / 'tests' / 'resources'


def get_default_path():
  """Return the default path."""
  return data_path()


def data_path() -> Path:
  """Return the data path."""
  return bin_project() / 'data'


def root_project() -> Path:
  """Return the root project path."""
  return bin_project().parent


def bin_project() -> Path:
  """Return the root project path."""
  return Path(__file__).parent
