from tradingbot.paths import root_project, config_path, data_path, file_exists
from pathlib import Path
import tempfile


def test_root_project():
  assert isinstance(root_project(), Path)


def test_config_path():
  assert config_path().exists()


def test_data_path():
  assert data_path().exists()


def test_file_exists():
  with tempfile.NamedTemporaryFile() as temp_file:
    # File exists
    temp_directory = Path(tempfile.mkstemp()[1])
    assert file_exists(temp_file.name, temp_directory)

  # File does not exist
  assert not file_exists('invalid.txt', config_path())
