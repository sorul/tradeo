from tradingbot.paths import config_path
import tradingbot.files as files
from pathlib import Path
import tempfile
import os
from unittest import mock


def test_get_successful_symbols(tmp_path):

  with open(tmp_path / 'successful_symbols.txt', 'w') as file:
    file.write('EURUSD\nUSDJPY\nGBPUSD')

  # Mock data_path to return the temporary file path
  with mock.patch('tradingbot.files.data_path') as mock_data_path:
    mock_data_path.return_value = tmp_path

    # Call the function to test
    result = files.get_successful_symbols()

  # Verify the result
  assert result == ['EURUSD', 'USDJPY', 'GBPUSD']


def test_file_exists():
  with tempfile.NamedTemporaryFile() as temp_file:
    # File exists
    temp_directory = Path(tempfile.mkstemp()[1])
    assert files.file_exists(temp_file.name, temp_directory)

  # File does not exist
  assert not files.file_exists('invalid.txt', config_path())


def test_try_load_json():
  with tempfile.NamedTemporaryFile() as temp_file:
    file = Path(temp_file.name)
    with open(file, 'w') as f:
      f.write('{"test": "test"}')
    data = files.try_load_json(file)
    assert data['test'] == 'test'


def test_try_read_file():
  with tempfile.TemporaryDirectory() as tmp_dir:

    # Create the temporary file inside the temporary directory
    temp_file = Path(tmp_dir) / "temp.txt"
    with open(temp_file, 'w') as f:
      f.write('test')

    assert 'test' == files.try_read_file(temp_file)

    os.remove(temp_file)

    assert '' == files.try_read_file(temp_file)


def test_try_remove_file():
  with tempfile.TemporaryDirectory() as tmp_dir:

    # Create the temporary file inside the temporary directory
    temp_file = Path(tmp_dir) / "temp.txt"
    temp_file.touch()

    # Make sure it exists before trying to remove it
    assert temp_file.exists()

    # Try to remove it
    assert files.try_remove_file(temp_file)

    # Validate that it no longer exists
    assert not temp_file.exists()
