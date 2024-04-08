from tradingbot.paths import config_path
import tradingbot.files as f
from pathlib import Path
import tempfile
import os


def test_file_exists():
  with tempfile.NamedTemporaryFile() as temp_file:
    # File exists
    temp_directory = Path(tempfile.mkstemp()[1])
    assert f.file_exists(temp_file.name, temp_directory)

  # File does not exist
  assert not f.file_exists('invalid.txt', config_path())


def test_try_load_json():
  with tempfile.NamedTemporaryFile() as temp_file:
    file = Path(temp_file.name)
    with open(file, 'w') as fi:
      fi.write('{"test": "test"}')
    data = f.try_load_json(file)
    assert data['test'] == 'test'


def test_try_read_file():
  with tempfile.TemporaryDirectory() as tmp_dir:

    # Create the temporary file inside the temporary directory
    filename = 'temp.txt'
    tmp_dir = Path(tmp_dir)
    temp_file = Path(tmp_dir) / filename
    with open(temp_file, 'w') as fi:
      fi.write('test')

    assert 'test' == f.try_read_file(temp_file)

    os.remove(temp_file)

    assert '' == f.try_read_file(temp_file)


def test_try_remove_file():
  with tempfile.TemporaryDirectory() as tmp_dir:

    # Create the temporary file inside the temporary directory
    temp_file = Path(tmp_dir) / 'temp.txt'
    temp_file.touch()

    # Make sure it exists before trying to remove it
    assert temp_file.exists()

    # Try to remove it
    assert f.try_remove_file(temp_file)

    # Validate that it no longer exists
    assert not temp_file.exists()


def test_write_file(tmp_path):
  file_path = Path(tmp_path)
  f.write_file('test.txt', 'test', file_path=file_path)
  with open(file_path / 'test.txt', 'r') as fi:
    assert fi.read() == 'test'


def test_remove_file(tmp_path):
  file_path = Path(tmp_path)
  file_name = 'test.txt'
  file = file_path / file_name
  file.touch()
  assert file.exists()
  f.remove_file(file_name, file_path=file_path)
  assert not file.exists()
