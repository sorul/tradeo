from tradingbot.paths import root_project, config_path, data_path
from pathlib import Path


def test_root_project():
  assert isinstance(root_project(), Path)


def test_config_path():
  assert config_path().exists()


def test_data_path():
  assert data_path().exists()
