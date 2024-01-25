from tradingbot import paths as p
from pathlib import Path


def test_root_project():
  assert isinstance(p.root_project(), Path)


def test_config_path():
  assert p.config_path().exists()


def test_data_path():
  assert p.data_path().exists()


def test_bash_path():
  assert p.bash_path().exists()


def test_tests_resources():
  assert p.test_resources().exists()
