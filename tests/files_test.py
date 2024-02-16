from tradingbot.paths import config_path
import tradingbot.files as f
from tradingbot.files import Files
from pathlib import Path
import tempfile
import os
from unittest.mock import patch


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

    assert 'test' == f.try_read_file(filename, tmp_dir)

    os.remove(temp_file)

    assert '' == f.try_read_file(filename, tmp_dir)


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


@patch('tradingbot.files.get_default_path')
def test_lock(mock_default_path, tmp_path):

  # Make data_path() return the temporary directory
  mock_default_path.return_value = tmp_path

  f.lock(Files.FOREX_LOCK)

  # Check that the file was written
  assert os.path.exists(tmp_path / Files.FOREX_LOCK.value)

  f.unlock(Files.FOREX_LOCK)

  # Check that the file was removed
  assert not os.path.exists(tmp_path / Files.FOREX_LOCK.value)


@patch('tradingbot.files.get_default_path')
def test_reset_successful_symbols_file(mock_default_path, tmp_path):

  # Make data_path() return the temporary directory
  mock_default_path.return_value = tmp_path

  # Create the file with some content
  mock_text = 'EURUSD\nUSDJPY\nGBPUSD'
  with open(tmp_path / Files.SUCCESSFUL_SYMBOLS.value, 'w') as file:
    file.write(mock_text)

  assert f.try_read_file(Files.SUCCESSFUL_SYMBOLS.value) == mock_text

  # Call to the function to test
  f.reset_successful_symbols_file()

  assert f.try_read_file(Files.SUCCESSFUL_SYMBOLS.value) == ''


@patch('tradingbot.files.get_default_path')
def test_reset_consecutive_times_down_file(mock_default_path, tmp_path):

  # Make data_path() return the temporary directory
  mock_default_path.return_value = tmp_path

  # Create the file with some content
  mock_text = '10'
  with open(tmp_path / Files.CONSECUTIVE_TIMES_DOWN.value, 'w') as file:
    file.write(mock_text)

  assert f.try_read_file(Files.CONSECUTIVE_TIMES_DOWN.value) == mock_text

  # Call to the function to test
  f.reset_consecutive_times_down_file()

  assert f.try_read_file(Files.CONSECUTIVE_TIMES_DOWN.value) == '0'


@patch('tradingbot.files.get_default_path')
def test_get_last_balance(mock_default_path, tmp_path):

  # Make data_path() return the temporary directory
  mock_default_path.return_value = tmp_path

  # Create the file with some content
  with open(tmp_path / Files.LAST_BALANCE.value, 'w') as file:
    file.write('100')

  # Call to the function to test
  assert f.get_last_balance() == 100


@patch('tradingbot.files.get_default_path')
def test_get_consecutive_times_down(mock_default_path, tmp_path):

  # Make data_path() return the temporary directory
  mock_default_path.return_value = tmp_path

  # Create the file with some content
  with open(tmp_path / Files.CONSECUTIVE_TIMES_DOWN.value, 'w') as file:
    file.write('10')

  # Call to the function to test
  assert f.get_consecutive_times_down() == 10


@patch('tradingbot.files.get_default_path')
def test_increment_consecutive_times_down(mock_default_path, tmp_path):

  # Make data_path() return the temporary directory
  mock_default_path.return_value = tmp_path

  # Create the file with some content
  with open(tmp_path / Files.CONSECUTIVE_TIMES_DOWN.value, 'w') as file:
    file.write('10')

  # Call to the function to test
  f.increment_consecutive_times_down()

  assert f.get_consecutive_times_down() == 11
